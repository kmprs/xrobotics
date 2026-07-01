function createNode(node) {

    const li = document.createElement("li");
    li.textContent = node.name;

    if (node.children && node.children.length > 0) {

        const ul = document.createElement("ul");

        node.children.forEach(child => {
            ul.appendChild(createNode(child));
        });

        li.appendChild(ul);
    }

    return li;
}

export function renderTree(containerId, tree) {

    const container = document.getElementById(containerId);

    container.innerHTML = "";

    const ul = document.createElement("ul");

    ul.appendChild(createNode(tree));

    container.appendChild(ul);
}
