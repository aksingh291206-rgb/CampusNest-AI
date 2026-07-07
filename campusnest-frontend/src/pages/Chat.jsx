import { useState, useRef, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../services/api";
import { motion } from "framer-motion";
import ResponseRenderer from "../components/ResponseRenderer";

function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef(null);

  const location = useLocation();
  const navigate = useNavigate();
  const sessionId = location.state?.sessionId;
  console.log("Session ID:", sessionId);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
        behavior: "smooth",
    });
    }, [messages]);

  const handleSend = async () => {
    if (message.trim() === "") return;

    const userMessage = message;

    setMessages(prev => [
        ...prev,
        {
            role: "user",
            text: userMessage,
        },
    ]);
    
    setMessage("");
    setLoading(true);
    try {
        const response = await api.post("/chat", {
            sessionId,
            message: userMessage,
        });

        console.log("Response from backend:");
        console.log(response.data);

        setMessages(prev => [
            ...prev,
            {
                role: "assistant",
                data: response.data,
            },
        ]);
    }
    catch (error) {
    console.error(error);

    setMessages((prev) => [
        ...prev,
        {
            role: "assistant",
            text: "Sorry, something went wrong. Please try again.",
        },
    ]);
}
    finally {
        setLoading(false);
    }
};

  const handleLogout = async () => {
    try {
        await api.post("/logout", {
            sessionId,
        });

        navigate("/");
    } catch (error) {
        console.error(error);
    }
};

  return (
    <motion.div
    className="min-h-screen bg-slate-950 flex flex-col"
    initial={{ opacity: 0, x: 40 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -40 }}
    transition={{ duration: 0.35 }}
    >
      {/* Header */}
      <div className="border-b border-cyan-500/20 p-5 flex items-center justify-between">

        <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-300 to-blue-500 bg-clip-text text-transparent">
            CampusNest AI
            </h1>

            <p className="text-slate-400 mt-1">
            Your Intelligent Hostel Assistant
            </p>
        </div>

        <button
            onClick={handleLogout}
            className="rounded-xl border border-red-500 px-4 py-2 text-red-400 transition hover:bg-red-500 hover:text-white"
        >
          Logout
        </button>

        </div>

        {loading && (
            <p className="text-center text-cyan-400 mb-4">
                CampusNest AI is thinking...
            </p>
        )}

    {/* Messages */}
    <div className="flex-1 overflow-y-auto p-6">
    {messages.map((msg, index) => (
        <div
        key={index}
        className={`mb-4 flex ${
            msg.role === "user" ? "justify-end" : "justify-start"
        }`}
        >
        <div
            className={`max-w-xl rounded-2xl px-4 py-3 ${
            msg.role === "user"
                ? "bg-cyan-600 text-white"
                : "bg-slate-800 text-cyan-300"
            }`}
        >
            {msg.role === "assistant" ? (
                <ResponseRenderer data={msg.data} />
            ) : (
                msg.text
            )}
        </div>
        </div>
    ))}

    <div ref={bottomRef}></div>
    </div>

      {/* Input Area */}
      <div className="border-t border-cyan-500/20 p-5 flex gap-4">
        <input
        type="text"
        placeholder="Type your message..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={(e) => {
            if (e.key === "Enter") {
            handleSend();
            }
        }}
        className="flex-1 rounded-xl border border-slate-700 bg-slate-800/70 px-4 py-3 text-white placeholder:text-slate-500 outline-none focus:border-cyan-400"
        />

        <button
          onClick={handleSend}
          disabled={loading}
          className="rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 px-6 text-white font-semibold"
        >
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </motion.div>
  );
}

export default Chat;