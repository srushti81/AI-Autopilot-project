export default function MicButton({ onClick, listening }) {
  return (
    <button
      onClick={onClick}
      className={`fixed bottom-6 right-6 p-4 rounded-full text-white shadow-lg ${
        listening ? "bg-red-600 animate-pulse" : "bg-blue-600"
      }`}
    >
      🎤
    </button>
  );
}
