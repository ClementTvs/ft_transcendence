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
        Conditions d'utilisation
      </h1>
      <p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-sm mb-10">
        Dernière mise à jour : 28 avril 2026
      </p>

      <div class="space-y-8 text-sm leading-relaxed">

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">1. Acceptation des conditions</h2>
          <p>En accédant à ft_transcendence ou en l'utilisant, vous acceptez d'être lié par les présentes conditions d'utilisation. Si vous n'acceptez pas ces conditions, veuillez ne pas utiliser la plateforme.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">2. Description du service</h2>
          <p>ft_transcendence est un réseau social orienté gaming développé dans le cadre du cursus 42. La plateforme permet de partager des publications, de discuter en temps réel, de suivre d'autres utilisateurs et de découvrir des jeux vidéo.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">3. Inscription et compte</h2>
          <p>Vous devez fournir des informations exactes lors de l'inscription. Vous êtes responsable de la sécurité de votre compte et de votre mot de passe. Vous devez nous notifier immédiatement de toute utilisation non autorisée de votre compte.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">4. Contenu utilisateur</h2>
          <p>Vous conservez la propriété du contenu que vous publiez. En publiant du contenu, vous nous accordez une licence non exclusive pour l'afficher sur la plateforme. Vous vous engagez à ne pas publier de contenu illégal, offensant, discriminatoire ou portant atteinte aux droits de tiers.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">5. Comportement</h2>
          <p>Vous vous engagez à utiliser la plateforme de manière respectueuse. Sont interdits : le harcèlement, le spam, l'usurpation d'identité, la diffusion de logiciels malveillants, et toute tentative de compromettre la sécurité du service.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">6. Suspension et résiliation</h2>
          <p>Nous nous réservons le droit de suspendre ou de supprimer votre compte en cas de violation des présentes conditions, sans préavis ni obligation de justification.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">7. Limitation de responsabilité</h2>
          <p>La plateforme est fournie « en l'état », sans garantie d'aucune sorte. Nous ne sommes pas responsables des dommages directs ou indirects liés à l'utilisation du service. Ce projet est réalisé dans un cadre éducatif (42).</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">8. Modifications</h2>
          <p>Nous pouvons modifier ces conditions à tout moment. Les modifications prennent effet dès leur publication sur la plateforme. Votre utilisation continue du service vaut acceptation des conditions modifiées.</p>
        </section>

        <section>
          <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-semibold mb-3">9. Contact</h2>
          <p>Pour toute question relative aux présentes conditions, vous pouvez nous contacter via la plateforme ou par les canaux de communication disponibles.</p>
        </section>

      </div>
    </div>
  </div>
</template>