/**
 * Collects all node names from a tree into a set (excluding root).
 * @param {Object} node - current tree node
 * @param {Set<string>} names - accumulator set of names
 * @param {boolean} isRoot - whether the current node is the root node
 * @returns {Set<string>} set of collected node names
 */
function collectNames(node, names = new Set(), isRoot = true) {
    if (!isRoot) {
        names.add(node.name);
    }
    if (node.children) {
        node.children.forEach(child => collectNames(child, names, false));
    }
    return names;
}

/**
 * Creates a DOM node representing a tree node recursively.
 * @param {Object} node - tree node
 * @param {Set<string>} otherNames - names existing in comparison tree
 * @param {string} extraClass - CSS class for missing/extra nodes
 * @param {boolean} isRoot - whether this is the root node
 * @returns {HTMLLIElement}
 */
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

/**
 * Renders a behavior tree into a container and highlights differences vs another tree.
 * @param {string} containerId - DOM element id
 * @param {Object} tree - primary tree to render
 * @param {Object} otherTree - comparison tree
 * @param {string} extraClass - CSS class for extra nodes
 */
export function renderTree(containerId, tree, otherTree, extraClass = "extra-robot") {
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    const otherNames = otherTree ? collectNames(otherTree) : new Set();

    const ul = document.createElement("ul");
    ul.appendChild(createNode(tree, otherNames, extraClass));
    container.appendChild(ul);
}

