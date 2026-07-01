const API_BASE = "http://localhost:8000";

export async function compareTrees(robotFile, humanFile, scenarioFile) {

    const formData = new FormData();

    formData.append("robotTree", robotFile);
    formData.append("humanTree", humanFile);
    formData.append("scenario", scenarioFile);

    const response = await fetch(`${API_BASE}/compare`, {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        throw new Error("Comparison failed.");
    }

    return await response.json();
}
