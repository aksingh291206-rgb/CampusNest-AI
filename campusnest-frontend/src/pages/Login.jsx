import { useState } from "react";
import api from "../services/api";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

function Login() {
  const [loginStep, setLoginStep] = useState(0);
  const [aiMessage, setAiMessage] = useState(
    "Welcome to CampusNest AI.\n\nClick Start to begin authentication."
  );

  const [sessionId, setSessionId] = useState("");
  const [studentId, setStudentId] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();


  const handleStart = async () => {
  console.log("Button clicked");

  try {
    // STEP 1 - Start Login
    if (loginStep === 0) {
      const response = await api.post("/login");

      console.log(response.data);

      setSessionId(response.data.sessionId);
      setAiMessage(response.data.message);

      setLoginStep(1);
      return;
    }

    // STEP 2 - Send Student ID
    if (loginStep === 1) {
      const response = await api.post("/send-student-id", {
        sessionId,
        studentId,
      });

      console.log(response.data);

      setAiMessage(response.data.message);

      setLoginStep(2);
      return;
    }

    // STEP 3 - Send Password
    if (loginStep === 2) {
      const response = await api.post("/send-password", {
        sessionId,
        password,
      });

      console.log(response.data);

      setAiMessage(response.data.message);

      if (response.data.message.toLowerCase().includes("success")) {
        setTimeout(() => {
          navigate("/chat", {
            state: {
              sessionId,
            },
          });
        }, 300);
      } else {
        setPassword("");
      }

      return;
    }
    } catch (error) {
    console.error(error);
  }
};

  return (
    <motion.div
    className="min-h-screen bg-slate-950 flex items-center justify-center"
    initial={{ opacity: 0, x: -40 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: 40 }}
    transition={{ duration: 0.35 }}>
      <div className="w-full max-w-md rounded-3xl border border-cyan-500/20 bg-slate-900/70 backdrop-blur-xl p-8">
        <h1 className="text-5xl font-bold text-center bg-gradient-to-r from-cyan-300 to-blue-500 bg-clip-text text-transparent">
          CampusNest AI
        </h1>

        <p className="mt-4 text-center text-slate-400">
          Intelligent Hostel Management Assistant
        </p>

        <div className="mt-10">
          {/* AI Status */}
          <div className="flex items-center justify-center gap-2">
            <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></div>

            <span className="text-sm uppercase tracking-widest text-emerald-400">
              AI Core Online
            </span>
          </div>

          {/* AI Message */}
          <div className="mt-8 rounded-2xl border border-cyan-500/20 bg-slate-800/60 p-6">
            <p className="text-center leading-7 text-cyan-300 whitespace-pre-line">
              {aiMessage}
            </p>
          </div>

          <AnimatePresence mode="wait">

        {loginStep === 1 && (
          <motion.div
            key="student-id"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="mt-8"
          >
            <input
              type="text"
              placeholder="Enter your Student ID"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-800/70 px-4 py-3 text-white placeholder:text-slate-500 outline-none focus:border-cyan-400"
            />
          </motion.div>
        )}

        {loginStep === 2 && (
          <motion.div
            key="password"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="mt-8"
          >
            <input
              type="password"
              placeholder="Enter your Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-800/70 px-4 py-3 text-white placeholder:text-slate-500 outline-none focus:border-cyan-400"
            />
          </motion.div>
        )}

      </AnimatePresence>

          {/* Button */}
          <div className="mt-8">
            <button
              onClick={handleStart}
              className="w-full rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 py-3 font-semibold text-white transition hover:scale-[1.02] hover:shadow-[0_0_25px_rgba(34,211,238,0.4)]"
            >
              {loginStep === 0 ? "Start" : "Continue"}
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default Login;