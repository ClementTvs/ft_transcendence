<template class="bg-rose-50">
  <div class="min-h-screen flex items-center justify-center">
    <div class="w-3xl h-3xl bg-rose-100 rounded-lg shadow-lg pt-15 pb-15">
        <div class="flex items-center justify-center">
            <h1 class="text-gray-600 font-bold mb-20 text-3xl">Se connecter :</h1>
        </div>
        <div class="flex items-center justify-center flex-col gap-20">
                <input class="text-black border rounded p-2 w-150" placeholder="Nom d'utilisateur"/>
                <input class="text-black border rounded p-2 w-150" placeholder="Mot de passe" />
                <div class="flex items-center justify-center">
                    <button class="border rounded bg-rose-200 hover:bg-rose-300 w-75 ml-10 mr-10">Connexion</button>
                    <button class="border rounded bg-rose-200 hover:bg-rose-300 w-75 ml-10 mr-10">Register</button>
                </div>
        </div>
    </div>
  </div>
</template>