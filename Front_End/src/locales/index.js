import en from './en.js'
import fr from './fr.js'

const translations = {
  en,
  fr
}

export function getTranslation(lang, key) {
  return translations[lang]?.[key] || key
}

export function getCurrentTranslations(lang) {
  return translations[lang] || translations.en
}

export default translations 