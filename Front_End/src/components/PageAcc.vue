<template>
  <div>
    <!-- Top Menu (App Bar) -->
    <v-app-bar app color="primary" dark>
      <v-spacer></v-spacer>
      <!-- Logout button -->
      <v-btn @click="logout" icon>
        <v-icon size="28">mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>

    <!-- SideBar Section -->
    <v-navigation-drawer expand-on-hover rail width="280">
      <v-list>
        <v-list-item
          prepend-avatar="https://cdn-icons-png.flaticon.com/512/3106/3106807.png"
          title="Mon Profil"
        ></v-list-item>
      </v-list>
      <v-divider />
      <v-list density="default" nav>
        <v-list-item :value="'dashboard'" prepend-icon="mdi-home" title="Dashboard" title-class="text-body-1">
        </v-list-item>
      </v-list>
      <v-divider />
      <v-list density="default" nav>
        <v-list-item :value="'cannibalisation'" prepend-icon="mdi-magnify" title="Cannibalisation" title-class="text-body-1">
        </v-list-item>
      </v-list>
      <v-divider />
      <v-list density="default" nav>
        <v-list-item :value="'scraping'" prepend-icon="mdi-web" title="Scraping" title-class="text-body-1">
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Main Content -->
    <v-main>
      <v-container class="d-flex flex-column pa-4" fluid>

        <v-row class="mb-4">
          <v-col cols="12" class="d-flex justify-end">
            <v-btn @click="scraper" color="#1A237E" size="large">
              <v-icon left size="24">mdi-plus</v-icon>
              Ajouter un produit
            </v-btn>
          </v-col>
        </v-row>

        <!-- Carte principale -->
        <v-row>
          <v-col v-for="product in products" :key="product.id" cols="12" sm="6">
            <v-card class="pa-6 custom-card" fill-height>
              <v-img :src="product.image" height="250px" cover></v-img>
              <v-card-title>
                {{ product.name }}
                <!-- Icône de suppression -->
                <v-btn @click="deleteProduct(product.id)" icon class="ml-2" color="red">
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </v-card-title>
              <v-card-subtitle>{{ product.brand }}</v-card-subtitle>
              <v-card-text class="card-text">
                <div>{{ product.description }}</div>
                <br/>
                <div class="text-h8" align="right">{{ product.reference }}</div>
                <br/>
                <div class="text-h6">{{ product.price }}</div>
              </v-card-text>
            </v-card>
          </v-col>

        </v-row>

      </v-container>
    </v-main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from "vue-router";

const router = useRouter();
const products = ref([]);

// Déconnexion
const logout = () => {
  console.log("Déconnexion...");
  localStorage.removeItem('authToken');
  router.push({ name: 'login' });
};

// Récupérer les produits
const fetchProducts = async () => {
  try {
    const response = await fetch('http://localhost:8000/products/');
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des produits');
    }
    products.value = await response.json();
  } catch (error) {
    console.error(error);
  }
};

// Appeler fetchProducts au montage du composant
onMounted(() => {
  fetchProducts();
});

const deleteProduct = async (productId) => {
  try {
    const response = await fetch(`http://localhost:8000/products/${productId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,  // Ajoutez l'authentification si nécessaire
      },
    });

    if (!response.ok) {
      throw new Error('Erreur lors de la suppression du produit');
    }

    // Retirer le produit de la liste localement après la suppression réussie
    products.value = products.value.filter(product => product.id !== productId);
    console.log('Produit supprimé avec succès');
  } catch (error) {
    console.error(error);
  }
};



const scraper = () => {
  router.push({ name: 'home' }); 
};
</script>

<style scoped>
/* Styles personnalisés */


.v-list-item-title {
  font-size: 16px;
}

.v-btn {
  font-size: 16px;
}

.v-text-field {
  font-size: 16px;
}
.v-main{
  min-width: 130vh;
}


</style>