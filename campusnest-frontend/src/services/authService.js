import api from "./api";

export async function sendMessage(sessionId, message) {
  return api.post(
    "/run_sse",
    {
      appName: "Campus_Nest_AI",
      userId: "user",
      sessionId,
      newMessage: {
        role: "user",
        parts: [
          {
            text: message,
          },
        ],
      },
      streaming: false,
    },
    {
      headers: {
        Accept: "text/event-stream",
      },
    }
  );
}