#!/usr/bin/env python3
"""
Script de test complet pour la messagerie instantanée.

Dépendances :
    pip install requests websockets

Usage :
    python test_messages.py
"""

import asyncio
import json
import subprocess
import requests
import websockets

BASE_URL = "http://localhost:8000"
WS_URL  = "ws://localhost:8000"

# ─── Couleurs terminal ────────────────────────────────────────────────────────

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):   print(f"  {GREEN}✓{RESET}  {msg}")
def err(msg):  print(f"  {RED}✗{RESET}  {msg}")
def info(msg): print(f"  {BLUE}→{RESET}  {msg}")
def section(title): print(f"\n{BOLD}{YELLOW}{'─'*50}\n  {title}\n{'─'*50}{RESET}")


# ─── Helpers REST ─────────────────────────────────────────────────────────────

def register(username: str, password: str, email: str) -> bool:
    r = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
    })
    if r.status_code == 200:
        ok(f"Compte créé : {username}")
        return True
    else:
        info(f"Compte déjà existant ou erreur pour {username} ({r.status_code})")
        return False


def login(username: str, password: str) -> str | None:
    r = requests.post(f"{BASE_URL}/api/auth/login", data={
        "username": username,
        "password": password,
    })
    if r.status_code == 200:
        token = r.json().get("access_token")
        ok(f"Connecté en tant que {username}")
        return token
    else:
        err(f"Login échoué pour {username} : {r.text}")
        return None


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_conversation(token: str, other_user_id: int) -> dict | None:
    r = requests.post(
        f"{BASE_URL}/api/messages/conversations/{other_user_id}",
        headers=auth_headers(token),
    )
    if r.status_code == 200:
        conv = r.json()
        ok(f"Conversation créée/récupérée (id={conv['id']})")
        return conv
    else:
        err(f"Erreur création conversation : {r.text}")
        return None


def list_conversations(token: str) -> list:
    r = requests.get(
        f"{BASE_URL}/api/messages/conversations",
        headers=auth_headers(token),
    )
    if r.status_code == 200:
        convs = r.json()
        ok(f"{len(convs)} conversation(s) trouvée(s)")
        for c in convs:
            last = c.get("last_message")
            last_content = last["content"] if last else "(aucun message)"
            print(f"     conv_id={c['id']} | avec={c['other_user']['username']} | dernier msg: {last_content!r} | non lus={c['unread_count']}")
        return convs
    else:
        err(f"Erreur liste conversations : {r.text}")
        return []


def get_messages(token: str, conv_id: int) -> list:
    r = requests.get(
        f"{BASE_URL}/api/messages/conversations/{conv_id}/messages",
        headers=auth_headers(token),
    )
    if r.status_code == 200:
        msgs = r.json()
        ok(f"{len(msgs)} message(s) dans la conversation {conv_id}")
        for m in msgs:
            print(f"     [{m['created_at']}] {m['sender']['username']}: {m['content']!r}  (lu={m['is_read']})")
        return msgs
    else:
        err(f"Erreur lecture messages : {r.text}")
        return []


def mark_as_read(token: str, conv_id: int):
    r = requests.put(
        f"{BASE_URL}/api/messages/conversations/{conv_id}/read",
        headers=auth_headers(token),
    )
    if r.status_code == 200:
        ok(f"Messages de la conversation {conv_id} marqués comme lus")
    else:
        err(f"Erreur mark as read : {r.text}")


def get_me(token: str) -> dict | None:
    r = requests.get(f"{BASE_URL}/api/users/me", headers=auth_headers(token))
    if r.status_code == 200:
        return r.json()
    return None


# ─── WebSocket ────────────────────────────────────────────────────────────────

async def test_websocket(token_alice: str, token_bob: str, conv_id: int):
    """
    Alice envoie un message à Bob via WebSocket.
    Bob le reçoit en temps réel.
    """
    received_by_bob = []
    received_by_alice = []

    async def alice(bob_id: int):
        url = f"{WS_URL}/api/messages/ws/chat?token={token_alice}"
        async with websockets.connect(url) as ws:
            ok("Alice connectée au WebSocket")
            # Attendre que Bob soit aussi connecté
            await asyncio.sleep(0.5)

            msg = {"to_user_id": bob_id, "conversation_id": conv_id, "content": "Salut Bob, tu me reçois ?"}
            await ws.send(json.dumps(msg))
            info(f"Alice envoie : {msg['content']!r}")

            # Attendre l'accusé de réception
            try:
                ack = await asyncio.wait_for(ws.recv(), timeout=3)
                received_by_alice.append(json.loads(ack))
                ok(f"Alice reçoit l'accusé : {received_by_alice[-1]['content']!r}")
            except asyncio.TimeoutError:
                err("Alice n'a pas reçu d'accusé de réception")

            await asyncio.sleep(0.5)

    async def bob():
        url = f"{WS_URL}/api/messages/ws/chat?token={token_bob}"
        async with websockets.connect(url) as ws:
            ok("Bob connecté au WebSocket")
            try:
                data = await asyncio.wait_for(ws.recv(), timeout=5)
                received_by_bob.append(json.loads(data))
                ok(f"Bob reçoit en temps réel : {received_by_bob[-1]['content']!r}")
            except asyncio.TimeoutError:
                err("Bob n'a pas reçu le message (timeout)")

    bob_profile = get_me(token_bob)
    bob_id = bob_profile["id"] if bob_profile else None
    if not bob_id:
        err("Impossible de récupérer l'id de Bob")
        return

    await asyncio.gather(bob(), alice(bob_id))

    return received_by_bob


# ─── Vérification chiffrement DB ─────────────────────────────────────────────

def check_db_encryption(plain_text: str):
    """
    Se connecte à la DB via docker compose exec et vérifie que le contenu
    stocké ne contient pas le message en clair.
    """
    try:
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "db",
             "psql", "-U", "postgres", "-d", "transcendence",
             "-c", "SELECT id, sender_id, content FROM messages ORDER BY id DESC LIMIT 5;"],
            capture_output=True,
            text=True,
            cwd="/Users/ziratya/Documents/Dev/42/Cursus/circle6/transendance",
        )

        if result.returncode != 0:
            err(f"Erreur psql : {result.stderr.strip()}")
            return

        output = result.stdout
        info("Contenu brut de la table messages (5 derniers) :")
        for line in output.strip().splitlines():
            print(f"     {line}")

        # Vérifier que le texte clair n'est PAS dans la DB
        if plain_text.lower() in output.lower():
            err(f"ÉCHEC — Le message en clair '{plain_text}' est lisible en DB !")
        else:
            ok(f"Le message en clair '{plain_text}' n'est PAS visible en DB")

        # Vérifier que le contenu ressemble à un token JWT (encodé)
        # Un JWT commence toujours par "eyJ" (base64 de {"...)
        if "eyJ" in output:
            ok("Le contenu stocké ressemble bien à un token encodé (eyJ...)")
        else:
            info("Le contenu ne ressemble pas à un JWT — vérifier crypto.py")

    except FileNotFoundError:
        err("docker non trouvé — assure-toi que Docker est installé et dans le PATH")


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main():
    print(f"\n{BOLD}=== TEST MESSAGERIE INSTANTANÉE ==={RESET}")

    # 1. Enregistrement
    section("1. Création des comptes")
    register("alice_test", "password123", "alice_test@test.com")
    register("bob_test",   "password123", "bob_test@test.com")

    # 2. Login
    section("2. Authentification")
    token_alice = login("alice_test", "password123")
    token_bob   = login("bob_test",   "password123")
    if not token_alice or not token_bob:
        err("Impossible de continuer sans tokens valides")
        return

    # 3. Récupérer l'id de Bob
    bob_profile = get_me(token_bob)
    if not bob_profile:
        err("Impossible de récupérer le profil de Bob")
        return
    bob_id = bob_profile["id"]
    info(f"Bob id={bob_id}")

    # 4. Créer une conversation
    section("3. Création de conversation")
    conv = create_conversation(token_alice, bob_id)
    if not conv:
        return
    conv_id = conv["id"]

    # 5. Lister les conversations
    section("4. Liste des conversations (vue Alice)")
    list_conversations(token_alice)

    # 5. Test WebSocket temps réel
    section("5. Test WebSocket temps réel")
    await test_websocket(token_alice, token_bob, conv_id)

    # 6. Vérifier le chiffrement en DB
    section("6. Vérification du chiffrement en DB")
    check_db_encryption("Salut Bob, tu me reçois ?")

    # 7. Lire l'historique
    section("7. Historique des messages (vue Bob)")
    get_messages(token_bob, conv_id)

    # 8. Marquer comme lu
    section("8. Marquer comme lu")
    mark_as_read(token_bob, conv_id)

    # 9. Vérifier le unread_count à 0
    section("9. Vérification unread_count après lecture")
    list_conversations(token_bob)

    print(f"\n{GREEN}{BOLD}=== TESTS TERMINÉS ==={RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
