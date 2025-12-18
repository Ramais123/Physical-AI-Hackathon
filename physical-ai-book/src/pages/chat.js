import React, { useState } from "react";
import { chatWithBook } from "../api";

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

const ask = async () => {
  if (!question.trim()) return;

  try {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    setAnswer(data.answer);
  } catch (e) {
    setAnswer("Backend Error!");
  }
}};
