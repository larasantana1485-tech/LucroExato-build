from pathlib import Path

root = Path("SantanaRemote")
ctl = root / "app/src/main/java/br/com/santana/remote/TvController.kt"
ui = root / "app/src/main/java/br/com/santana/remote/MainActivity.kt"
gradle = root / "app/build.gradle.kts"
readme = root / "README.md"

def change(p, old, new):
    s = p.read_text(encoding="utf8")
    if s.count(old) != 1:
        raise ValueError("Padrao ausente/duplicado em " + str(p) + ": " + old[:70])
    p.write_text(s.replace(old, new, 1), encoding="utf8")

change(ctl, '                } else if (id.startsWith("youtube_search")) {',
'''                } else if (id.startsWith("voice_channel_")) {
                    feedback = "A TV não conseguiu sintonizar esse canal. Confira a antena e o número disponível."
                } else if (id.startsWith("youtube_search")) {''')

change(ctl, '    fun executeVoiceCommand(heard: String) {',
'''    /** Tune the tuner directly; no digit-by-digit pointer simulation. */
    private fun tuneVoiceChannel(number: String) {
        if (!connected) {
            feedback = "TV desconectada. Reconecte antes de trocar de canal."
            ensureConnected()
            return
        }
        request("ssap://tv/openChannel", JSONObject().put("channelNumber", number),
            id = "voice_channel_" + requestCounter.incrementAndGet())
        feedback = "Solicitada a sintonia do canal " + number + "."
    }

    /** Paces bounded volume actions; stops requests from a stale websocket epoch. */
    private fun adjustVoiceVolume(up: Boolean, steps: Int) {
        if (!connected) {
            feedback = "TV desconectada. Reconecte antes de ajustar o volume."
            ensureConnected()
            return
        }
        val session = epoch
        for (step in 0 until steps) {
            main.postDelayed({
                if (connected && session == epoch) volume(up)
            }, step * 350L)
        }
        feedback = "Solicitado: " + (if (up) "aumentar" else "diminuir") +
            " volume " + steps + (if (steps == 1) " vez." else " vezes.")
    }

    fun executeVoiceCommand(heard: String) {
        when (val action = VoiceCommandParser.parse(heard)) {
            is SpokenTvAction.TuneChannel -> { tuneVoiceChannel(action.number); return }
            is SpokenTvAction.VolumeSteps -> { adjustVoiceVolume(action.up, action.steps); return }
            is SpokenTvAction.SearchYouTube -> { searchYouTube(action.query); return }
            is SpokenTvAction.TooManyVolumeSteps -> {
                feedback = "Máximo de 20 etapas por comando. Você pediu " + action.requested + "."
                return
            }
            SpokenTvAction.PowerOn -> {
                if (connected) feedback = "A TV já está conectada."
                else wake() // Wake-on-LAN requires TV MAC and Wi-Fi wake enabled.
                return
            }
            SpokenTvAction.NotRecognized -> Unit
        }''')

change(ui,
 'putExtra(android.speech.RecognizerIntent.EXTRA_PROMPT, "Diga o que deseja fazer na TV")',
 'putExtra(android.speech.RecognizerIntent.EXTRA_PROMPT, "Ex.: canal cinco, aumentar volume cinco vezes, buscar receitas no YouTube")')
change(gradle, 'versionCode = 4', 'versionCode = 5')
change(gradle, 'versionName = "0.2.1-tela-unica"', 'versionName = "0.2.2-voz-natural"')
change(gradle, '    debugImplementation("androidx.compose.ui:ui-tooling")',
 '    testImplementation("junit:junit:4.13.2")\n    debugImplementation("androidx.compose.ui:ui-tooling")')
if readme.exists():
    readme.write_text(readme.read_text(encoding="utf8") +
       "\n\n## Versão 0.2.2: comandos de voz naturais\n"
       "- Diga 'coloca no canal cinco' ou 'vai para o canal 25'.\n"
       "- Diga 'aumenta o volume cinco vezes' ou 'abaixa o som em 3 passos'.\n"
       "- Diga 'procura vídeos de receitas no YouTube'.\n"
       "- Diga 'liga a TV': Wake-on-LAN com MAC e configuração de ligar via Wi-Fi na TV.\n"
       "A pesquisa do YouTube pode não funcionar no firmware da TV.\n"
       "O app mantém uma tela única e o touchpad sempre visível.\n", encoding="utf8")
print("Santana Remote 0.2.2: patch de voz natural aplicado")
