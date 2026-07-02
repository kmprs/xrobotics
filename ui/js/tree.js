function collectNames(node, names = new Set(), isRoot = true) {
    if (!isRoot) {
        names.add(node.name);
    }
    if (node.children) {
        node.children.forEach(child => collectNames(child, names, false));
    }
    return names;
}

function createNode(node, otherNames, extraClass, isRoot = true) {
    const li = document.createElement("li");
    li.textContent = node.name;

    if (!isRoot && !otherNames.has(node.name)) {
        li.classList.add("tree-node-extra", extraClass);
    }

    if (node.children && node.children.length > 0) {
        const ul = document.createElement("ul");
        node.children.forEach(child => {
            ul.appendChild(createNode(child, otherNames, extraClass, false));
        });
        li.appendChild(ul);
    }
    return li;
}

export function renderTree(containerId, tree, otherTree, extraClass = "extra-robot") {
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    const otherNames = otherTree ? collectNames(otherTree) : new Set();

    const ul = document.createElement("ul");
    ul.appendChild(createNode(tree, otherNames, extraClass));
    container.appendChild(ul);
}

