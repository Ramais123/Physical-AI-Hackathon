export async function chatWithBook(question) {
  const res = await fetch(
    `${process.env.REACT_APP_API_URL}/chat`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    }
  );
  return res.json();
}
