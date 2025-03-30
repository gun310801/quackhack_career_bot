export const sendCareerQuery = async (question) => {
  try {
    const response = await fetch(`http://localhost:8000/career-query/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error("Error sending query:", error);
  }
};
