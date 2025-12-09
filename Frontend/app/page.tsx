"use client";
import { Input } from "@/components/ui/input";
import { useState, useRef, useEffect } from "react";
import { SendHorizontal } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (input.trim() === "") return;

    // 1. Add User Message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: "user",
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // 2. Add Loading Message
    const loadingId = "loading-" + Date.now();
    setMessages((prev) => [
      ...prev,
      {
        id: loadingId,
        content: "Analyzing Clinical Trials & Market Data...",
        role: "assistant",
      },
    ]);

    try {
      // 3. Call Backend
      const response = await fetch("http://localhost:8000/generate_report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input }),
      });

      const data = await response.json();

      // 4. Update with Real Report
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingId ? { ...msg, content: data.report } : msg
        )
      );
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingId
            ? { ...msg, content: "Error: Ensure Backend (uvicorn) is running." }
            : msg
        )
      );
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex h-screen w-full flex-col bg-[#343541] text-gray-100 font-sans">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="mx-auto max-w-4xl space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`rounded-2xl px-6 py-4 max-w-[90%] ${
                  message.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-[#444654] shadow-xl"
                }`}
              >
                {/* RENDER REPORT HERE */}
                {message.role === "assistant" ? (
                  <article className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {String(message.content || "")}
                    </ReactMarkdown>
                  </article>
                ) : (
                  <div>{message.content}</div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-white/10 bg-[#343541] p-4">
        <div className="mx-auto max-w-3xl relative">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search for a molecule (e.g. Aspirin for Lung Cancer)..."
            className="h-14 w-full rounded-xl bg-[#40414F] pl-4 pr-12 text-white border-none shadow-lg focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSendMessage}
            className="absolute bottom-3 right-3 p-2 text-gray-400 hover:text-white transition-colors"
          >
            <SendHorizontal size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
