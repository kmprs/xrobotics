import { compareTrees } from "./api.js";
import { renderTree } from "./tree.js";

const compareButton = document.getElementById("compareBtn");

const robotInput = document.getElementById("robotTree");
const humanInput = document.getElementById("humanTree");
const scenarioInput = document.getElementById("scenario");

const video = document.querySelector("video");

const explanationsContainer = document.querySelector(".explanations");

compareButton.addEventListener("click", compare);

async function compare() {

    const robotFile = robotInput.files[0];
    const humanFile = humanInput.files[0];
    const scenarioFile = scenarioInput.files[0];

    if (!robotFile || !humanFile || !scenarioFile) {

        alert("Please select all required files.");
        return;
    }

    compareButton.disabled = true;
    compareButton.textContent = "Comparing...";

    try {

        const result = await compareTrees(
            robotFile,
            humanFile,
            scenarioFile
        );

        renderTree("robotTreeView", result.robotTree);
        renderTree("humanTreeView", result.humanTree);

        renderVideo(result.video);

        renderExplanations(result.explanations);

    }
    catch (err) {

        console.error(err);

        alert(err.message);

    }
    finally {

        compareButton.disabled = false;
        compareButton.textContent = "Compare Trees";

    }

}

function renderVideo(path) {

    video.src = path;
    video.load();

}

function renderExplanations(explanations) {

    explanationsContainer.innerHTML = "";

    if (explanations.length === 0) {

        explanationsContainer.innerHTML = `
            <p class="placeholder">
                Nothing to explain in this simulation run 😄
            </p>
        `;

        return;
    }

    explanations.forEach(exp => {

        const card = document.createElement("div");

        card.className = "explanation-card";

        card.innerHTML = `
            <div class="question">
                ${exp.question}
            </div>

            <div class="answer">
                ${exp.answer}
            </div>
        `;

        explanationsContainer.appendChild(card);

    });

}
