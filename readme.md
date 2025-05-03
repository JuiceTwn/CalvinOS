mermaid
    graph TD
        subgraph Node [🦾 Node (Peripheral)]
            mic[🎤 Mic Input]
            vad[VAD + Wake Word]
            rec[🎙️ Capture Audio Chunk]
            wsSend[📡 Send Audio to Core]
            wsRecv[📥 Receive TTS Audio]
            play[🔊 Play Response]
            fallback[🟡 Fallback Logic (if no core)]
            mic --> vad --> rec --> wsSend
            wsRecv --> play
            fallback -.-> play
        end

        subgraph Core [🧠 Core (Brain)]
            wsReceive[🔁 Receive Audio]
            stt[🧠 STT (Whisper)]
            nlp[NLP + Intent Detection]
            skill[🧞 Run Skill or LLM]
            tts[🗣️ TTS (Piper/Coqui)]
            wsReturn[🚀 Send Back TTS Audio]
            voiceMatch[🔐 Voiceprint Matching]
            memory[📒 User Profile + Logs]

            wsReceive --> stt --> nlp --> skill --> tts --> wsReturn
            stt --> voiceMatch --> memory
            nlp --> memory
            skill --> memory
        end

        wsSend --> wsReceive
        wsReturn --> wsRecv