<template>
  <div>
    <v-form ref="domUrlForm" @submit.prevent="createRecipe">
      <div>
        <v-card-title class="headline">{{ $t('recipe.create-recipe-from-text') }}</v-card-title>
        <v-card-text>
          <p>{{ $t('recipe.create-recipe-from-text-description') }}</p>
          <v-container class="pa-0">
            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="recipeText"
                  :label="$t('recipe.enter-recipe-text')"
                  :placeholder="$t('recipe.recipe-text-placeholder')"
                  outlined
                  auto-grow
                  rows="6"
                  :disabled="loading"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions v-if="recipeText">
          <div>
            <p style="width: 250px">
              <BaseButton rounded block type="submit" :loading="loading" />
            </p>
            <p>
              <v-checkbox
                v-model="shouldTranslate"
                hide-details
                :label="$t('recipe.should-translate-description')"
                :disabled="loading"
              />
            </p>
            <p v-if="loading" class="mb-0">
              {{ $t('recipe.please-wait-processing') }}
            </p>
          </div>
        </v-card-actions>
      </div>
    </v-form>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  ref,
  toRefs,
  useContext,
  useRoute,
  useRouter,
} from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { VForm } from "~/types/vuetify";

export default defineComponent({
  setup() {
    const state = reactive({
      loading: false,
    });

    const { i18n } = useContext();
    const api = useUserApi();
    const route = useRoute();
    const router = useRouter();
    const groupSlug = computed(() => route.value.params.groupSlug || "");

    const domUrlForm = ref<VForm | null>(null);
    const recipeText = ref("");
    const shouldTranslate = ref(true);

    async function createRecipe() {
      if (!recipeText.value.trim()) {
        return;
      }

      state.loading = true;
      const translateLanguage = shouldTranslate.value ? i18n.locale : undefined;
      const { data, error } = await api.recipes.createOneFromText(recipeText.value, translateLanguage);
      if (error || !data) {
        alert.error(i18n.tc("events.something-went-wrong"));
        state.loading = false;
      } else {
        router.push(`/g/${groupSlug.value}/r/${data}`);
      }
    }

    return {
      ...toRefs(state),
      domUrlForm,
      recipeText,
      shouldTranslate,
      createRecipe,
    };
  },
});
</script>
