<template>
  <v-container class="d-flex">
    <!-- Top Menu (App Bar) -->
    <v-app-bar app color="primary" dark>
      <v-spacer></v-spacer>
      <!-- Logout button -->
      <v-btn @click="logout" icon>
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>

    <!-- SideBar Section -->
    <v-navigation-drawer expand-on-hover rail>
      <v-list>
        <v-list-item
          prepend-avatar="https://cdn-icons-png.flaticon.com/512/3106/3106807.png"
          title="Mon Profil"
        ></v-list-item>
      </v-list>
      <v-divider />
      <v-list density="compact" nav>
        <v-list-item :value="'dashboard'" prepend-icon="mdi-home" title="Dashboard">
        </v-list-item>
      </v-list>
      <v-divider />
      <v-list density="compact" nav>
        <v-list-item :value="'cannibalisation'" prepend-icon="mdi-magnify" title="Cannibalisation">
        </v-list-item>
      </v-list>
      <v-divider />
      <v-list density="compact" nav>
        <v-list-item :value="'scraping'" prepend-icon="mdi-web" title="Scraping">
      </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Main Content Section -->
    <v-container class="d-flex flex-column pa-4" fluid>
      <v-btn class="mb-4" color="blue-grey-darken-1" @click="goToHomePage">
        Revenir vers la page d'accueil
      </v-btn>
      <v-card width="1200" class="pa-6 custom-card">
        <v-card-text>
          <v-row justify="start">
            <!-- Barcode input instead of URL input -->
            <v-col cols="12" sm="8" class="d-flex align-center">
              <v-text-field
                v-model="barcode"
                label="Code-barres du produit (13 chiffres)"
                placeholder="Ex: 6192484100407"
                outlined
                dense
                class="mr-2 combined-width"
                maxlength="13"
                type="text"
              ></v-text-field>
              <v-icon class="mdi-icon" color="primary" style="font-size: 28px; margin-top: -20px;">
                mdi-barcode
              </v-icon>
            </v-col>
          </v-row>

          <!-- ID/Class Input Section for photo -->
          <v-row justify="start" class="mt-4">
            <v-col cols="12" sm="8" class="d-flex align-center">
              <!-- Cadre autour de "Pour la photo" -->
              <v-sheet class="custom-frame d-flex align-center justify-center">
                <span class="custom-text"> L'image : </span>
              </v-sheet>

              <!-- Champ input et sélecteur pour la photo -->
              <v-text-field
                v-model="photoTextInput"
                placeholder="Entrez votre sélecteur"
                outlined
                dense
                class="mr-2 fixed-width"
              ></v-text-field>
            </v-col>
          </v-row>

          <!-- ID/Class Input Section for name -->
          <v-row justify="start" class="mt-4">
            <v-col cols="12" sm="8" class="d-flex align-center">
              <!-- Cadre autour de "Pour le nom" -->
              <v-sheet class="custom-frame d-flex align-center justify-center">
                <span class="custom-text"> Le nom : </span>
              </v-sheet>

              <!-- Champ input et sélecteur pour le nom -->
              <v-text-field
                v-model="nameTextInput"
                placeholder="Entrez votre sélecteur"
                outlined
                dense
                class="mr-2 fixed-width"
              ></v-text-field>
            </v-col>
          </v-row>

          <!-- ID/Class Input Section for brand -->
          <v-row justify="start" class="mt-4">
            <v-col cols="12" sm="8" class="d-flex align-center">
              <!-- Cadre autour de "Pour la marque" -->
              <v-sheet class="custom-frame d-flex align-center justify-center">
                <span class="custom-text"> La marque : </span>
              </v-sheet>

              <!-- Champ input et sélecteur pour la marque -->
              <v-text-field
                v-model="brandTextInput"
                placeholder="Entrez votre sélecteur"
                outlined
                dense
                class="mr-2 fixed-width"
              ></v-text-field>
            </v-col>
          </v-row>
          <!-- ID/Class Input Section for reference -->
          <v-row justify="start" class="mt-4">
            <v-col cols="12" sm="8" class="d-flex align-center">
              <!-- Cadre autour de "Pour la référence" -->
              <v-sheet class="custom-frame d-flex align-center justify-center">
                <span class="custom-text"> La référence : </span>
              </v-sheet>

              <!-- Champ input et sélecteur pour la référence -->
              <v-text-field
                v-model="referenceTextInput"
                placeholder="Entrez votre sélecteur"
                outlined
                dense
                class="mr-2 fixed-width"
              ></v-text-field>
            </v-col>
          </v-row>


          <!-- ID/Class Input Section for price -->
          <v-row justify="start" class="mt-4">
            <v-col cols="12" sm="8" class="d-flex align-center">
              <!-- Cadre autour de "Pour le prix" -->
              <v-sheet class="custom-frame d-flex align-center justify-center">
                <span class="custom-text"> Le prix : </span>
              </v-sheet>

              <!-- Champ input et sélecteur pour le prix -->
              <v-text-field
                v-model="priceTextInput"
                placeholder="Entrez votre sélecteur"
                outlined
                dense
                class="mr-2 fixed-width"
              ></v-text-field>
            </v-col>
          </v-row>

          <!-- ID/Class Input Section for description -->
          <v-row justify="start" class="mt-4">
            <v-col cols="12" sm="8" class="d-flex align-center">
              <!-- Cadre autour de "Pour la description" -->
              <v-sheet class="custom-frame d-flex align-center justify-center">
                <span class="custom-text"> La description : </span>
              </v-sheet>

              <!-- Champ input et sélecteur pour la description -->
              <v-text-field
                v-model="descriptionTextInput"
                placeholder="Entrez votre sélecteur"
                outlined
                dense
                class="mr-2 fixed-width"
              ></v-text-field>

            </v-col>
          </v-row>

          <!-- Get Result Button -->
          <v-btn class="saveButton" @click="getScrapedData">Get Result</v-btn>
          <v-row v-if="productInfo">
            <v-col cols="12">
              <v-img :src="productInfo.image" alt="Product Image" max-width="400px"></v-img>
              <v-card>
                <v-card-title>{{ productInfo.name }}</v-card-title>
                <v-card-subtitle>{{ productInfo.brand }}</v-card-subtitle>
                <v-card-text>{{ productInfo.reference }}</v-card-text>
                <v-card-text>{{ productInfo.price }}</v-card-text>
                <v-card-text>{{ productInfo.description }}</v-card-text>
              </v-card>
            </v-col>
          </v-row>
          <br/>
          <v-btn class="saveButton" @click="saveProduct" v-if="productInfo">Save it </v-btn>

        </v-card-text>
      </v-card>
    </v-container>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router'; 
import axios from 'axios';

const router = useRouter();
// Remove url, add barcode
const barcode = ref('');
const photoTextInput = ref('');
const nameTextInput = ref('');
const brandTextInput = ref('');
const referenceTextInput = ref('');
const priceTextInput = ref('');
const descriptionTextInput = ref('');

if (!localStorage.getItem('authToken')) {
  router.push({ name: 'login' });
}
const goToHomePage = () => {
  router.push({ name: 'pageacc' }); // Redirige vers la page d'accueil (PageAcc.vue)
};
const logout = () => {
  console.log("Déconnexion...");
  localStorage.removeItem('authToken');
  router.push({ name: 'login' });
};

const productInfo = ref(null); // Variable pour stocker les informations du produit
// Fonction pour appeler l'API scraping
const getScrapedData = async () => {
  if (!barcode.value || barcode.value.length !== 13 || !/^\d{13}$/.test(barcode.value)) {
    alert('Veuillez entrer un code-barres valide (13 chiffres).');
    return;
  }
  // Build the product URL from the barcode
  const url = `https://pharma-shop.tn/protection-superieure-a-spf-50/5535-clarenia-claresun-ecran-gel-creme-toucher-sec-spf50-50ml-${barcode.value}.html`;
  try {
    const response = await axios.get('http://localhost:8000/scrape', {
      params: {
        url: url,
        image_selector: photoTextInput.value,
        name_selector: nameTextInput.value,
        brand_selector: brandTextInput.value,
        reference_selector: referenceTextInput.value, // Ajout de la référence
        price_selector: priceTextInput.value,
        description_selector: descriptionTextInput.value,
      },
    });

    // Enregistrer les données récupérées
    productInfo.value = response.data.product_info;
    console.log(productInfo.value);
  } catch (error) {
    console.error('Erreur lors du scraping:', error);
    alert('Une erreur est survenue lors du scraping');
  }
};

// Fonction pour enregistrer le produit dans la base de données
const saveProduct = async () => {
  try {
    const response = await axios.post('http://localhost:8000/products/', {
      image: productInfo.value.image,
      name: productInfo.value.name,
      brand: productInfo.value.brand,
      reference: productInfo.value.reference,
      price: productInfo.value.price,
      description: productInfo.value.description,
    });

    if (response.status === 200) {
      alert('Produit enregistré avec succès !');
    }
  } catch (error) {
    console.error('Erreur lors de l\'enregistrement du produit:', error);
    alert('Une erreur est survenue lors de l\'enregistrement du produit');
  }
};

</script>

<style scoped>
.custom-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.mdi-icon {
  color: #123b64;
}

.mr-2 {
  margin-right: 8px;
}

.ml-2 {
  margin-left: 5px;
}

.saveButton {
  float: right;
  color: rgb(251, 251, 255);
  background-color: navy;
}

/* Ajout d'une largeur pour l'URL */
.combined-width {
  width: 520px; /* Largeur du champ URL, */
}

/* Largeur fixe pour les champs de texte et les sélecteurs */
.fixed-width {
  width: 400px; /* Ajustez la largeur selon vos besoins */
  min-width: 400px;
  max-width: 400px;
}

/* Styles pour le texte "Pour la photo" */
.custom-text {
  color: navy; /* Couleur bleu marine */
  font-weight: bolder; /* Texte en gras */
  font-size: 16px; /* Taille de police plus grande */
  white-space: nowrap; /* Empêche le texte de passer à la ligne */
  text-decoration: underline;
}

/* Cadre autour de "Pour la photo" */
.custom-frame {
  background-color: #f5f5f5; /* Couleur de fond légère */
  border: 1px solid #ddd; /* Bordure légère */

  padding: 8px 16px; /* Espacement interne */
  margin-right: 16px; /* Espacement à droite */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Ombre légère */
  height: 50px; /* Hauteur fixe pour correspondre aux champs input et select */
  display: flex;
  align-items: center; /* Centrer verticalement le texte */
  min-width: 150px; /* Largeur minimale pour le cadre */
  margin-top: -22px; /* Décalage vers le haut pour aligner avec le champ input */
}
</style>