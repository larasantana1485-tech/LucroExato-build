package br.com.santana.remote

import java.text.Normalizer
import java.util.Locale

/** Commands parsed locally. The Android speech service only converts speech to text. */
internal sealed class SpokenTvAction {
    data class TuneChannel(val number: String) : SpokenTvAction()
    data class VolumeSteps(val up: Boolean, val steps: Int) : SpokenTvAction()
    data class SearchYouTube(val query: String) : SpokenTvAction()
    data class TooManyVolumeSteps(val requested: Int) : SpokenTvAction()
    object PowerOn : SpokenTvAction()
    object NotRecognized : SpokenTvAction()
}

internal object VoiceCommandParser {
    private val units = mapOf(
        "zero" to 0, "um" to 1, "uma" to 1, "dois" to 2, "duas" to 2,
        "tres" to 3, "quatro" to 4, "cinco" to 5, "seis" to 6,
        "sete" to 7, "oito" to 8, "nove" to 9, "dez" to 10,
        "onze" to 11, "doze" to 12, "treze" to 13, "quatorze" to 14,
        "catorze" to 14, "quinze" to 15, "dezesseis" to 16,
        "dezessete" to 17, "dezoito" to 18, "dezenove" to 19,
        "vinte" to 20, "trinta" to 30, "quarenta" to 40,
        "cinquenta" to 50, "sessenta" to 60, "setenta" to 70,
        "oitenta" to 80, "noventa" to 90, "cem" to 100,
        "cento" to 100, "duzentos" to 200, "trezentos" to 300,
        "quatrocentos" to 400, "quinhentos" to 500,
        "seiscentos" to 600, "setecentos" to 700,
        "oitocentos" to 800, "novecentos" to 900
    )

    private fun fold(input: String): String = Normalizer.normalize(
        input.trim().lowercase(Locale.forLanguageTag("pt-BR")), Normalizer.Form.NFD
    ).replace(Regex("[\\u0300-\\u036f]"), "")
        .replace(Regex("[!?;,]+"), " ")
        .replace(Regex("\\s+"), " ").trim()

    private fun number(text: String): Int? {
        val cleaned = text.trim().replace(Regex("\\s+(?:por favor|agora|da tv)$"), "")
        cleaned.toIntOrNull()?.let { return it }
        if (cleaned.isBlank()) return null
        val words = cleaned.split(Regex("\\s+")).filter { it != "e" }
        if (words.isEmpty() || words.any { it !in units }) return null
        return words.sumOf { units.getValue(it) }
    }

    fun parse(utterance: String): SpokenTvAction {
        val speech = fold(utterance)
        if (speech.isEmpty()) return SpokenTvAction.NotRecognized

        if (Regex("^(?:liga|ligar|ligue|acende|acender) (?:a |o )?(?:tv|televisao|televisor)$")
                .matches(speech)) return SpokenTvAction.PowerOn

        // Search requests do NOT use the TV's on-screen keyboard.
        val searchVerb = "(?:pesquisar|pesquisa|pesquise|buscar|busca|busque|procurar|procura|procure|encontrar|encontra|encontre)"
        val youtubeBefore = Regex("^$searchVerb (?:no |pelo )?youtube (.+)$").find(speech)
        val youtubeAfter = Regex("^$searchVerb (.+?) (?:no |pelo )?youtube$").find(speech)
        val searchText = (youtubeBefore?.groupValues?.get(1) ?: youtubeAfter?.groupValues?.get(1))
            ?.replace(Regex("^(?:videos? (?:de|sobre) |de |sobre |por |o |a )"), "")
            ?.trim()
        if (!searchText.isNullOrBlank()) return SpokenTvAction.SearchYouTube(searchText)

        val channel = Regex("\\bcanal (?:numero )?(.+)$").find(speech)?.groupValues?.get(1)
        if (channel != null) {
            val channelNumber = if (Regex("\\d{1,3}[.-]\\d{1,2}").matches(channel)) channel
                else number(channel)?.toString()
            if (channelNumber != null) return SpokenTvAction.TuneChannel(channelNumber)
        }

        val sound = Regex("\\b(?:volume|som|audio)\\b").containsMatchIn(speech)
        val increasing = Regex("\\b(?:aumenta|aumentar|aumente|sobe|subir|eleva|elevar)\\b")
            .containsMatchIn(speech)
        val decreasing = Regex("\\b(?:abaixa|abaixar|abaixe|baixa|diminuir|diminui|diminua|reduz|reduzir|desce)\\b")
            .containsMatchIn(speech)
        if (sound && (increasing xor decreasing)) {
            val remaining = Regex("\\b(?:volume|som|audio)\\b(?: em)? (.+)$")
                .find(speech)?.groupValues?.get(1)
            val stepsText = remaining?.replace(Regex("\\s+(?:vezes|vez|passos|pontos|niveis)$"), "")
            val steps = stepsText?.let(::number) ?: 1
            if (steps > 20) return SpokenTvAction.TooManyVolumeSteps(steps)
            if (steps > 0) return SpokenTvAction.VolumeSteps(increasing, steps)
        }
        return SpokenTvAction.NotRecognized
    }
}
