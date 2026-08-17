import { useState, useRef, useEffect } from "react";

const API_URL = import.meta.env.VITE_API_URL;
const BAR_COUNT = 28;

const REASON_LABELS = {
  off_topic_or_no_match: "Nothing in the corpus grounds that question",
  ungrounded_answer: "Couldn't verify the answer against retrieved sources",
};

export default function App() {
  const [status, setStatus] = useState("idle"); // idle | recording | processing | done | mic_error
  const [result, setResult] = useState(null);

  const mediaRecorder = useRef(null);
  const chunks = useRef([]);
  const barRefs = useRef([]);
  const audioCtx = useRef(null);
  const analyser = useRef(null);
  const rafId = useRef(null);

  const drawLoop = () => {
    if (!analyser.current) return;
    const data = new Uint8Array(analyser.current.frequencyBinCount);
    analyser.current.getByteFrequencyData(data);
    const step = Math.floor(data.length / BAR_COUNT);
    barRefs.current.forEach((el, i) => {
      if (!el) return;
      const v = data[i * step] / 255;
      el.style.transform = `scaleY(${Math.max(0.12, v)})`;
    });
    rafId.current = requestAnimationFrame(drawLoop);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      audioCtx.current = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioCtx.current.createMediaStreamSource(stream);
      analyser.current = audioCtx.current.createAnalyser();
      analyser.current.fftSize = 128;
      source.connect(analyser.current);
      drawLoop();

      mediaRecorder.current = new MediaRecorder(stream);
      chunks.current = [];
      mediaRecorder.current.ondataavailable = (e) => chunks.current.push(e.data);
      mediaRecorder.current.onstop = handleStop;
      mediaRecorder.current.start();
      setStatus("recording");
    } catch (err) {
      setStatus("mic_error");
    }
  };

  const stopRecording = () => {
    mediaRecorder.current.stop();
    cancelAnimationFrame(rafId.current);
    audioCtx.current?.close();
    setStatus("processing");
  };

  const handleStop = async () => {
    const blob = new Blob(chunks.current, { type: "audio/webm" });
    const formData = new FormData();
    formData.append("audio", blob, "query.webm");

    try {
      const res = await fetch(`${API_URL}/ask`, { method: "POST", body: formData });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: String(err) });
    }
    setStatus("done");
  };

  useEffect(() => () => cancelAnimationFrame(rafId.current), []);

  const isRecording = status === "recording";
  const isProcessing = status === "processing";

  return (
    <div className="min-h-screen bg-ink text-sand flex flex-col items-center justify-center px-6 py-16">
      {/* Eyebrow */}
      <p className="font-mono text-xs tracking-[0.25em] text-lagoon uppercase mb-3">
        HH Goa 2026 · Voice RAG
      </p>

      {/* Title */}
     <h1 className="text-5xl sm:text-6xl font-bold text-sand mb-2">
  <span className="font-display">No </span>
  <span className="font-devanagari font-extrabold text-brass">खामोशी</span>
</h1>
<p className="text-sand-dim text-sm mb-12 text-center max-w-sm">
  No silence until there's something grounded to say. Ask a question in Hindi.
</p>

      {/* Mic button */}
      <button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isProcessing}
        className={`relative w-24 h-24 rounded-full flex items-center justify-center
          transition-all duration-300 disabled:opacity-60
          ${isRecording ? "bg-lagoon" : "bg-laterite hover:bg-laterite-dim"}`}
        style={isRecording ? { animation: "ring-pulse 1.8s ease-out infinite" } : {}}
      >
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
          <rect x="9" y="2" width="6" height="12" rx="3" fill="#0B1E22" />
          <path
            d="M5 11a7 7 0 0014 0M12 18v3"
            stroke="#0B1E22"
            strokeWidth="2"
            strokeLinecap="round"
            fill="none"
          />
        </svg>
      </button>

      <p className="font-mono text-xs text-sand-dim mt-4 mb-8 tracking-wide">
        {status === "idle" && "TAP TO ASK"}
        {status === "recording" && "LISTENING — TAP TO STOP"}
        {status === "processing" && "TRANSCRIBING · RETRIEVING · GENERATING"}
        {status === "done" && "DONE — TAP TO ASK AGAIN"}
        {status === "mic_error" && "MIC ACCESS DENIED"}
      </p>

      {/* Tide bar — signature element */}
      <div className="w-full max-w-xs h-10 flex items-end justify-center gap-[3px] mb-10">
        {Array.from({ length: BAR_COUNT }).map((_, i) => (
          <div
            key={i}
            ref={(el) => (barRefs.current[i] = el)}
            className={`w-1 h-full rounded-full origin-bottom ${
              isRecording ? "bg-lagoon" : isProcessing ? "shimmer" : "bg-laterite-dim bar-idle"
            }`}
            style={
              !isRecording
                ? { animationDelay: `${i * 70}ms`, transform: "scaleY(0.3)" }
                : undefined
            }
          />
        ))}
      </div>

      {/* Result card */}
      {result && (
        <div className="w-full max-w-xl bg-ink-2 rounded-2xl border border-laterite-dim/40 p-6 space-y-4">
          {result.error && (
            <p className="text-laterite font-mono text-sm">⚠ {result.error}</p>
          )}

          {result.query && (
            <p className="font-mono text-xs text-sand-dim">
              <span className="text-lagoon">HEARD ·</span> {result.query}
            </p>
          )}

          {result.refused ? (
            <div className="border-l-2 border-brass pl-4 py-1">
              <p className="text-brass font-medium">Declined to answer</p>
              <p className="text-sand-dim text-sm mt-1">
                {REASON_LABELS[result.reason] || result.reason}
              </p>
            </div>
          ) : (
            result.answer && (
              <p className="font-display text-xl leading-relaxed text-sand">
                {result.answer}
              </p>
            )
          )}

          {result.sources?.length > 0 && (
            <div className="border-t border-laterite-dim/30 pt-4 space-y-1.5">
              <p className="font-mono text-[11px] tracking-widest text-sand-dim uppercase mb-2">
                Sources
              </p>
              {result.sources.map((s, i) => (
                <p key={i} className="font-mono text-xs text-sand-dim truncate">
                  [{i + 1}] {s}
                </p>
              ))}
            </div>
          )}

          {result.timings && (
            <p className="font-mono text-[11px] text-lagoon pt-2">
              total {result.timings.total_ms?.toFixed(0)}ms · retrieval{" "}
              {result.timings.retrieval_ms?.toFixed(0)}ms
            </p>
          )}
        </div>
      )}

      <p className="font-mono text-[11px] text-sand-dim/60 tracking-widest mt-16">
        #RAGInGoa
      </p>
    </div>
  );
}