from pathlib import Path

root = Path("SantanaRemote")
ctl = root / "app/src/main/java/br/com/santana/remote/TvController.kt"
ui = root / "app/src/main/java/br/com/santana/remote/MainActivity.kt"
gradle = root / "app/build.gradle.kts"

def swap(path, old, new):
    s = path.read_text(encoding="utf-8")
    if old not in s:
        raise RuntimeError("Trecho ausente: " + str(path) + " : " + old[:60])
    path.write_text(s.replace(old, new, 1), encoding="utf-8")

swap(ctl,
    '    var keyboardFocused by mutableStateOf(false)',
    '    var foregroundAppId by mutableStateOf("")\n        private set\n    var keyboardFocused by mutableStateOf(false)')
swap(ctl,
    '        keyboardFocused = false\n        status = "Desconectada"',
    '        keyboardFocused = false\n        foregroundAppId = ""\n        status = "Desconectada"')
swap(ctl,
    '            request("ssap://com.webos.service.ime/registerRemoteKeyboard",',
    '            request("ssap://com.webos.applicationManager/getForegroundAppInfo",\n                JSONObject().put("subscribe", true), id = "foreground_1", type = "subscribe")\n            request("ssap://com.webos.service.ime/registerRemoteKeyboard",')
swap(ctl,
    '                } else if (id.startsWith("keyboard") || id.startsWith("text")) {',
    '                } else if (id.startsWith("youtube_search")) {\n                    feedback = "A TV recusou a pesquisa direta do YouTube nesta versão do webOS."\n                } else if (id.startsWith("keyboard") || id.startsWith("text")) {')
swap(ctl,
    '            id == "keyboard_1" -> {',
    '            id == "foreground_1" -> ui { foregroundAppId = payload.optString("appId") }\n            id == "keyboard_1" -> {')
swap(ctl,
    '    fun sendText(text: String) {',
    '''    fun sendSmartText(text: String) {
        if (foregroundAppId.contains("youtube", ignoreCase = true)) searchYouTube(text)
        else sendText(text)
    }
    /** Requests the YouTube app to open search results, bypassing its custom keyboard. */
    fun searchYouTube(text: String) {
        val query = text.trim()
        if (!connected) { feedback = "Conecte à TV antes de pesquisar."; return }
        if (query.isBlank()) { feedback = "Digite algo para pesquisar no YouTube."; return }
        val appId = apps.firstOrNull {
            it.name.contains("YouTube", ignoreCase = true) ||
                it.id.contains("youtube", ignoreCase = true)
        }?.id ?: "youtube.leanback.v4"
        val encoded = java.net.URLEncoder.encode(query, "UTF-8")
        val params = JSONObject().put("target", "q=$encoded")
        request("ssap://com.webos.applicationManager/launch",
            JSONObject().put("id", appId).put("params", params),
            id = "youtube_search_" + requestCounter.incrementAndGet())
        feedback = "Pesquisa solicitada ao YouTube. Confira na TV se os resultados abriram."
    }
    fun sendText(text: String) {''')
swap(ui,
    '    val clipboard = (clipboardContext.getSystemService(android.content.Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager)',
    '    val clipboard = (clipboardContext.getSystemService(android.content.Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager)\n    val youtubeActive = tv.foregroundAppId.contains("youtube", ignoreCase = true)')
swap(ui,
    '        if (tv.keyboardFocused) {\n            Text("● Campo de texto detectado na TV", color = Success, fontSize = 13.sp)\n        } else {',
    '        if (youtubeActive) {\n            Text("YouTube detectado: pesquisa direta, sem usar o teclado da TV.", color = Success, fontSize = 12.sp)\n        } else if (tv.keyboardFocused) {\n            Text("● Campo de texto detectado na TV", color = Success, fontSize = 13.sp)\n        } else {')
swap(ui,
    'keyboardActions = KeyboardActions(onDone = { tv.sendText(text); keyboard?.hide() }),',
    'keyboardActions = KeyboardActions(onDone = { tv.sendSmartText(text); keyboard?.hide() }),')
swap(ui,
    'Surface(onClick = { tv.sendText(text); keyboard?.hide() }, modifier = Modifier.fillMaxWidth().height(59.dp),',
    'Surface(onClick = { tv.sendSmartText(text); keyboard?.hide() }, modifier = Modifier.fillMaxWidth().height(59.dp),')
swap(ui,
    'Text("Enviar texto para a TV", color = White, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)',
    'Text(if (youtubeActive) "Pesquisar no YouTube" else "Enviar texto para a TV", color = White, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)')
swap(ui,
    '''        Spacer(Modifier.height(14.dp))
        Feedback(tv)
    }
}

@Composable
private fun ConnectionDialog''',
    '''        Spacer(Modifier.height(10.dp))
        if (!youtubeActive) {
            OutlinedButton(onClick = { tv.searchYouTube(text); keyboard?.hide() },
                modifier = Modifier.fillMaxWidth().height(53.dp),
                shape = RoundedCornerShape(24.dp),
                border = BorderStroke(1.dp, Pale)) {
                Icon(Icons.Filled.Search, contentDescription = null, tint = Pale)
                Spacer(Modifier.width(7.dp))
                Text("Pesquisar direto no YouTube", color = White)
            }
        }
        Spacer(Modifier.height(6.dp))
        Text("Alguns aplicativos usam teclado próprio. A busca direta pode reabrir o YouTube e depende do webOS.",
            color = Gray, fontSize = 11.sp)
        Spacer(Modifier.height(14.dp))
        Feedback(tv)
    }
}

@Composable
private fun ConnectionDialog''')
swap(gradle, 'versionCode = 1', 'versionCode = 2')
v = gradle.read_text(encoding="utf-8")
swap(gradle, 'versionName = "0.1.1-teste"' if "0.1.1-teste" in v else 'versionName = "0.1.0-teste"', 'versionName = "0.1.2-youtube"')
print("Busca direta do YouTube aplicada.")
