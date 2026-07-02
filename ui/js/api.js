const API_BASE = "http://localhost:8000";


/**
 * Sends behavior tree files to backend for comparison.
 * @param {File} robotFile - robot behavior tree XML file
 * @param {File} humanFile - human behavior tree XML file
 * @param {File} scenarioFile - scenario JSON file
 * @returns {Promise<Object>} comparison result from backend
 */
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
