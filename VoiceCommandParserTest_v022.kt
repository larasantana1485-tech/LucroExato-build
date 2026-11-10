package br.com.santana.remote
import org.junit.Assert.assertEquals
import org.junit.Test

class VoiceCommandParserTest {
    @Test fun channelNumbers() {
        assertEquals(SpokenTvAction.TuneChannel("5"), VoiceCommandParser.parse("coloca no canal 5"))
        assertEquals(SpokenTvAction.TuneChannel("5"), VoiceCommandParser.parse("coloca no canal cinco"))
        assertEquals(SpokenTvAction.TuneChannel("25"), VoiceCommandParser.parse("muda para o canal vinte e cinco"))
        assertEquals(SpokenTvAction.TuneChannel("5.1"), VoiceCommandParser.parse("vai pro canal 5.1"))
        assertEquals(SpokenTvAction.NotRecognized, VoiceCommandParser.parse("próximo canal"))
    }
    @Test fun repeatedVolume() {
        assertEquals(SpokenTvAction.VolumeSteps(true, 5), VoiceCommandParser.parse("aumenta o volume cinco vezes"))
        assertEquals(SpokenTvAction.VolumeSteps(false, 3), VoiceCommandParser.parse("abaixa o som em 3 passos"))
        assertEquals(SpokenTvAction.VolumeSteps(true, 1), VoiceCommandParser.parse("aumenta volume"))
        assertEquals(SpokenTvAction.TooManyVolumeSteps(21), VoiceCommandParser.parse("diminui volume 21 vezes"))
    }
    @Test fun youtubeQueries() {
        assertEquals(SpokenTvAction.SearchYouTube("receitas"), VoiceCommandParser.parse("procura vídeos de receitas no YouTube"))
        assertEquals(SpokenTvAction.SearchYouTube("musica gospel"), VoiceCommandParser.parse("pesquisar no YouTube música gospel"))
        assertEquals(SpokenTvAction.SearchYouTube("desenhos"), VoiceCommandParser.parse("buscar desenhos no youtube"))
    }
    @Test fun powerOnIsDistinct() {
        assertEquals(SpokenTvAction.PowerOn, VoiceCommandParser.parse("liga a TV"))
        assertEquals(SpokenTvAction.PowerOn, VoiceCommandParser.parse("ligar a televisão"))
        assertEquals(SpokenTvAction.NotRecognized, VoiceCommandParser.parse("desligar TV"))
    }
}