<script setup>
import { ref, onMounted } from 'vue'

const dark = ref(false)

onMounted(() => {
  dark.value = localStorage.getItem('theme') === 'dark'
})
</script>

<template>
  <div :class="dark ? 'bg-gray-950 text-gray-200' : 'bg-rose-50 text-gray-700'" class="min-h-screen">
    <div class="max-w-3xl mx-auto px-6 py-12">

      <!-- Back -->
      <router-link
        to="/"
        :class="dark ? 'text-gray-500 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'"
        class="inline-flex items-center gap-1.5 text-sm mb-8 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
        </svg>
        Retour
      </router-link>

      <!-- Header -->
      <h1 :class="dark ? 'text-white' : 'text-gray-900'" class="text-3xl font-bold mb-2">
        Politique de confidentialité
      </h1>
      <p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-sm mb-10">
        Dernière mise à jour : 28 avril 2026
      </p>

      <div class="space-y-8 text-sm leading-relaxed">

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">1. Données collectées</h2>
          <p>Nous collectons les données que vous fournissez lors de l'inscription (nom d'utilisateur, email, mot de passe hashé) ainsi que le contenu que vous publiez (posts, commentaires, messages). Des données techniques comme votre adresse IP et votre user-agent peuvent être enregistrées à des fins de sécurité.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">2. Utilisation des données</h2>
          <p>Vos données sont utilisées pour fournir et améliorer le service : affichage de votre profil, gestion des interactions sociales (follow, likes, commentaires), messagerie en temps réel, et personnalisation de votre expérience (suggestions, fil d'actualité).</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">3. Stockage et sécurité</h2>
          <p>Vos données sont stockées sur nos serveurs. Les mots de passe sont hashés et ne sont jamais stockés en clair. Nous mettons en œuvre des mesures techniques raisonnables pour protéger vos données, mais aucun système n'est totalement infaillible.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">4. Partage des données</h2>
          <p>Nous ne vendons pas vos données personnelles. Les informations de votre profil public (nom d'utilisateur, avatar, bio) sont visibles par les autres utilisateurs. Nous ne partageons vos données avec des tiers que si la loi l'exige.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">5. Cookies et stockage local</h2>
          <p>Nous utilisons le localStorage du navigateur pour stocker votre token d'authentification et vos préférences (thème sombre). Aucun cookie de suivi tiers n'est utilisé.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">6. Vos droits</h2>
          <p>Conformément au RGPD, vous disposez d'un droit d'accès, de rectification et de suppression de vos données personnelles. Vous pouvez modifier vos informations depuis votre profil ou demander la suppression de votre compte.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">7. Services tiers</h2>
          <p>La plateforme utilise l'API RAWG.io pour afficher des informations sur les jeux vidéo. Lorsque vous effectuez une recherche de jeux, des requêtes sont envoyées directement à ce service. Nous vous invitons à consulter leur politique de confidentialité.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">8. Modifications</h2>
          <p>Cette politique peut être mise à jour à tout moment. Les modifications seront publiées sur cette page avec une date de mise à jour révisée.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">9. Contact</h2>
          <p>Pour exercer vos droits ou pour toute question relative à vos données, contactez-nous via la plateforme.</p>
        </section>

      </div>
    </div>
  </div>
</template>