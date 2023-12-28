#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#include <algorithm>
#include <optional>
#include <map>
#include <vector>
#include <tuple>
#include <queue>
#include <stdexcept>
#include <limits>

namespace py = pybind11;

struct TupleComparator {
    bool operator()(const std::tuple<int, int, int>& lhs, const std::tuple<int, int, int>& rhs) const {
        return std::get<2>(lhs) < std::get<2>(rhs);
    }
};

// Edge structure to store cost
struct Edge {
    int node1;
    int node2;
    int key;
    int cost;
    int id;

    Edge() : node1(0), node2(0), key(0), cost(0), id(0) {};
    Edge(int n1, int n2, int k, int c, int i) : node1(n1), node2(n2), key(k), cost(c), id(i) {};
};

// Node structure to store color
struct Node {
    int id;
    int posx;
    int posy;

    Node() : id(-1), posx(-1), posy(-1) {};
    Node(int i, int x, int y) : id(i), posx(x), posy(y) {};
};

// Graph class
class Graph {
private:
    std::map<int, Edge> allEdges;
    std::map<int, std::map<int, std::map<int, Edge>>> adjacencyList;
    std::map<int, Node> allNodes;

public:
    // Function to add an edge with a specified cost
    void addEdge(int v1, int v2, int key, int cost, int id) {
        py::print("adding edge: ", v1, v2, key, cost, id);

        adjacencyList[v1][v2][key] = Edge(v1, v2, key, cost, id);
        adjacencyList[v2][v1][key] = Edge(v2, v1, key, cost, id);
        allEdges[id] = Edge(v1, v2, key, cost, id);
    };

    void addEdge(int v1, int v2, int cost, int id) {
        py::print("adding edge: ", v1, v2, cost, id);

        auto keyToEdge = adjacencyList[v1][v2];
        int newKey = 0;
        for (const auto& pair : keyToEdge) {
            if (pair.first > newKey) newKey = pair.first;
        };
        newKey++;

        adjacencyList[v1][v2][newKey] = Edge(v1, v2, newKey, cost, id);
        adjacencyList[v2][v1][newKey] = Edge(v2, v1, newKey, cost, id);
        allEdges[id] = Edge(v1, v2, newKey, cost, id);
    };

    void removeEdge(int v1, int v2, int key, int id) {
        py::print("remove edge: ", v1, v2, key, id);
        adjacencyList[v1][v2].erase(key);
        adjacencyList[v2][v1].erase(key);
        allEdges.erase(id);
    };

    void addNode(int id, int posx, int posy) {
        py::print("adding node: ", id, posx, posy);

        auto it = allNodes.find(id);
        if (it == allNodes.end()) {
            allNodes[id] = Node(id, posx, posy);
        };
    };

    void removeNode(int node) {
        py::print("remove node: ", node);
        std::vector<Edge> edges = getEdges(node);
        for (const auto& edge : edges) {
            allEdges.erase(edge.id);
        };

        std::map<int, std::map<int, Edge>> nodeToKeysToEdges = adjacencyList[node];
        adjacencyList.erase(node);

        for (const auto& pair : nodeToKeysToEdges) {
            adjacencyList[pair.first].erase(node);
        };

        allNodes.erase(node);
    };

    std::vector<Edge> getAllEdges() {
        std::vector<Edge> edges;
        for (const auto& pair : allEdges) {
            edges.push_back(pair.second);
        };
        return edges;
    };

    std::vector<Edge> getEdges(int node) {
        std::vector<Edge> edges;
        py::print("found", adjacencyList[node].size(), "edges for", node);
        for (const auto& pair1 : adjacencyList[node]) {
            for (const auto& pair2 : pair1.second) {
                edges.push_back(pair2.second);
            };
        };
        return edges;
    };

    std::vector<Edge> getEdges(int node1, int node2) {
        std::vector<Edge> edges;
        for (const auto& pair : adjacencyList[node1][node2]) {
            edges.push_back(pair.second);
        };
        return edges;
    };

    Edge getMinCostEdge(int node1, int node2) {
        py::print("found", adjacencyList[node1][node2].size(), "edges between", node1, "and", node2);
        std::optional<Edge> edge;
        int minCost = 100;
        for (const auto& pair : adjacencyList[node1][node2]) {
            if (pair.second.cost < minCost) {
                py::print(pair.second.cost, "is smaller than", minCost);
                edge = pair.second;
                minCost = edge->cost;
            } else {
                py::print(pair.second.cost, "is not smaller than", minCost);
            };
        };

        if (!edge) {
            throw std::runtime_error("expected to find edge between node " + std::to_string(node1) + " and " + std::to_string(node2));
        }
        py::print("found edge");
        return *edge;
    };

    Edge getMinCostEdge(int node1, int node2, std::set<int> exceptEdges) {
        py::print("found", adjacencyList[node1][node2].size(), "edges between", node1, "and", node2);
        std::optional<Edge> edge;
        int minCost = 100;
        for (const auto& pair : adjacencyList[node1][node2]) {
            if (pair.second.cost < minCost) {
                // filter out edges from exceptEdges
                if (exceptEdges.contains(pair.second.id)) continue;

                edge = pair.second;
                minCost = edge->cost;
            };
        };

        if (!edge) {
            throw std::runtime_error("expected to find edge between node " + std::to_string(node1) + " and " + std::to_string(node2));
        }

        return *edge;
    };

    std::vector<int> getAllEdgeIds() {
        std::vector<int> edges;
        for (const auto& pair : allEdges) {
            edges.push_back(pair.first);
        };
        return edges;
    };

    std::vector<Node> getAllNodes() {
        std::vector<Node> nodes;
        for (const auto& pair : allNodes) {
            nodes.push_back(pair.second);
        };
        return nodes;
    };

    std::vector<int> getAllNodeIds() {
        std::vector<int> nodes;
        for (const auto& pair : allNodes) {
            nodes.push_back(pair.first);
        };
        return nodes;
    };

    std::tuple<int, int> maxPos() {
        int maxx = 0;
        int maxy = 0;
        for (const auto& node : allNodes) {
            if (node.second.posx > maxx) {
                maxx = node.second.posx;
            };
            if (node.second.posy > maxy) {
                maxy = node.second.posy;
            };
        };
        std::tuple<int, int> maxPos(maxx, maxy);
        return maxPos;
    };

    template <typename NodeContainer>
    int mergeNodes(const NodeContainer& nodes) {
        std::vector<int> allNodes = getAllNodeIds();
        int newNode = (*std::max_element(allNodes.begin(), allNodes.end())) + 1;
        addNode(newNode, -1, -1);

        std::map<int, Edge> edges;
        for (const auto& node : nodes) {
            std::vector<Edge> edgesOfNode = getEdges(node);
            for (const auto& edge : edgesOfNode) {
                edges[edge.id] = edge;
            }
        };

        for (const auto& node : nodes) {
            removeNode(node);
        };

        for (const auto& pair : edges) {
            auto it = std::find(nodes.begin(), nodes.end(), pair.second.node2);
            if (it != nodes.end()) {
                addEdge(newNode, newNode, pair.second.cost, pair.second.id);
            } else {
                addEdge(newNode, pair.second.node2, pair.second.cost, pair.second.id);
            };
        };

        return newNode;
    };
};

class Solver {
private:
    Graph graph;
    Graph searchGraph;
    std::map<int, int> nodeToComponent;
    std::map<int, std::set<int>> components;
    std::map<int, std::map<int, int>> nodeToPredecessor;
    std::set<int> multicut;


public:
    void loadGraph(const std::vector<std::tuple<int, int, int>>& nodes, const std::vector<std::tuple<int, int, int, int, int>>& edges) {
        for (const auto& node : nodes) {
            graph.addNode(std::get<0>(node), std::get<1>(node), std::get<2>(node));
        };

        for (const auto& edge : edges) {
            graph.addEdge(std::get<0>(edge), std::get<1>(edge), std::get<2>(edge), std::get<3>(edge), std::get<4>(edge));
        };

        buildSearchGraph();
    };

    void loadSearchGraph(const std::vector<std::tuple<int, int, int>>& nodes, const std::vector<std::tuple<int, int, int, int, int>>& edges) {
        py::print("loading search graph");

        for (const auto& node : nodes) {
            searchGraph.addNode(std::get<0>(node), std::get<1>(node), std::get<2>(node));
        }

        for (const auto& edge : edges) {
            searchGraph.addEdge(std::get<0>(edge), std::get<1>(edge), std::get<2>(edge), std::get<3>(edge), std::get<4>(edge));
        }

        py::print("loading search graph finished");
    };

    void buildSearchGraph() {
        std::tuple<int, int> maxPos = graph.maxPos();
        int maxx;
        int maxy;
        std::tie(maxx, maxy) = maxPos;

        int n = 0;
        for (size_t x = 0; x < maxx; x++) {
            for (size_t y = 0; y < maxy; y++) {
                searchGraph.addNode(n, x, y);
                n++;
            }
        }
        searchGraph.addNode(n, -1, -1);

        // implementation not finished
    };

    int getNewComponentId() {
        auto it = components.rbegin();
        int greatestKey = (it != components.rend()) ? it->first : 0;
        return greatestKey + 1;
    };

    std::tuple<int, int> getLowestCostPredecessor(int node) {
        int minCostPredecessor = node;
        int minCost = 0;
        py::print("node", node, "has", nodeToPredecessor[node].size(), "predecessor");

        for (const auto& [predecessor, cost] : nodeToPredecessor[node]) {
            if (node == predecessor) continue;
            py::print("predecessor", predecessor, "has cost", cost);
            if (cost < minCost) {
                minCostPredecessor = predecessor;
                minCost = cost;
            };
        };

        return {minCostPredecessor, minCost};
    };

    std::tuple<int, int> getLowestCostPredecessor(int node, int exceptNode) {
        int minCostPredecessor;
        int minCost = 0;

        for (const auto& [predecessor, cost] : nodeToPredecessor[node]) {
            if (node == predecessor) continue;
            if (predecessor == exceptNode) continue;
            if (cost < minCost) {
                minCostPredecessor = predecessor;
                minCost = cost;
            };
        };

        return { minCostPredecessor, minCost };
    };

    void handleSelfEdges() {
        py::print("handling self edges");

        for (const Edge& edge : searchGraph.getAllEdges()) {
            if (edge.node1 == edge.node2) {
                if (edge.cost < 0) {
                    multicut.insert(edge.id);
                };

                auto it1 = nodeToPredecessor[edge.node1].find(edge.node2);
                if (it1 != nodeToPredecessor[edge.node1].end()) {
                    nodeToPredecessor[edge.node1].erase(edge.node2);
                };

                searchGraph.removeEdge(edge.node1, edge.node2, edge.key, edge.id);
            };
        };
    };

    void updateComponentCost(int componentId) {
        py::print("updating costs for component ", componentId);

        std::set<int> nodes = components[componentId];
        std::vector<int> startNodes;
        for (const auto& node : nodes) {
            if (nodeToPredecessor[node].size() < 2) {
                startNodes.push_back(node);
            };
        };

        std::queue<std::tuple<int, int>> nodeQueue;
        for (const auto& startNode : startNodes) {
            nodeQueue = std::queue<std::tuple<int, int>>();
            int predecessor = startNode;
            int secondNode = nodeToPredecessor[startNode].begin()->first;
            nodeQueue.push({secondNode, predecessor});
            while (!nodeQueue.empty()) {
                auto [currentNode, predecessor] = nodeQueue.front();
                if (currentNode == predecessor) continue;
                nodeQueue.pop();
                int predecessorCost = std::get<1>(getLowestCostPredecessor(predecessor, currentNode));
                int edgeCost = searchGraph.getMinCostEdge(currentNode, predecessor).cost;
                nodeToPredecessor[currentNode][predecessor] = predecessorCost + edgeCost;

                for (const auto& pair : nodeToPredecessor[currentNode]) {
                    if (pair.first == predecessor) continue;
                    nodeQueue.push({ pair.first, currentNode });
                };
            };
        };
    };

    std::tuple<std::vector<std::tuple<int, Edge>>, int> findPath(int startNode, int endNode) {
        py::print("finding path from ", startNode, " to ", endNode);

        if (startNode == endNode) {
            std::vector<std::tuple<int, Edge>> emptyPath;
            return { emptyPath, 0 };
        };

        std::map<int, Edge> predecessors;
        std::vector<std::tuple<int, int>> nodeQueue;
        auto currentNode = startNode;
        int cost = 0;
        std::set<int> foundEdges;
        std::set<int> foundNodes;
        foundNodes.insert(startNode);

        while (true) {
            for (const auto& pair : nodeToPredecessor[currentNode]) {
                int neighbor = pair.first;

                if (foundNodes.contains(neighbor)) continue;

                Edge minEdge = searchGraph.getMinCostEdge(currentNode, neighbor, foundEdges);

                int totalNeighborCost = cost + minEdge.cost;
                predecessors[neighbor] = minEdge;

                // mark edge as
                foundEdges.insert(minEdge.id);


                // mark node as found
                foundNodes.insert(neighbor);

                if (neighbor == endNode) {
                    // found cycle
                    Edge edge = predecessors[endNode];
                    int predecessorNode = edge.node1;
                    std::vector<std::tuple<int, Edge>> path;

                    while (predecessorNode != startNode) {
                        path.emplace_back(predecessorNode, edge);
                        edge = predecessors[predecessorNode];
                        predecessorNode = edge.node1;
                    };
                    path.emplace_back(startNode, edge);
                    std::reverse(path.begin(), path.end());

                    return { path, totalNeighborCost };
                };
                nodeQueue.emplace_back(neighbor, totalNeighborCost);
            };

            if (nodeQueue.empty()) break;
            std::tie(currentNode, cost) = nodeQueue.back();
            nodeQueue.pop_back();
        };

        throw std::runtime_error("findPath expected to find a path, but no path was found.");
    };

    void handleCycle(std::vector<std::tuple<int, Edge>> cycle, bool createComponent = true) {
        py::print("handling cycle");

        // remove cut edges from graph and add them to the multicut
        for (const auto& [node, edge] : cycle) {
            searchGraph.removeEdge(edge.node1, edge.node2, edge.key, edge.id);
            multicut.insert(edge.id);
        };

        // create necessary variables
        std::set<int> cycleNodesSet;
        std::transform(cycle.begin(), cycle.end(), std::inserter(cycleNodesSet, cycleNodesSet.begin()),
            [](const auto& tuple) { return std::get<0>(tuple); });

        std::set<int> componentIdsSet;
        std::transform(cycleNodesSet.begin(), cycleNodesSet.end(), std::inserter(componentIdsSet, componentIdsSet.begin()),
            [this](const auto& node) { return nodeToComponent[node]; });

        std::set<int> allNodesSet;
        for (const auto& componentId : componentIdsSet) {
            std::set_union(allNodesSet.begin(), allNodesSet.end(), components[componentId].begin(), components[componentId].end(), std::inserter(allNodesSet, allNodesSet.begin()));
            // remove component
            components.erase(componentId);
        };

        // nonCycleNodesSet = allNodesSet - cycleNodesSet
        std::set<int> nonCycleNodesSet;
        std::set_difference(allNodesSet.begin(), allNodesSet.end(),
            cycleNodesSet.begin(), cycleNodesSet.end(), std::inserter(nonCycleNodesSet, nonCycleNodesSet.begin()));

        // remove component
        for (const auto& node : allNodesSet) {
            nodeToComponent.erase(node);
        };

        // merge nodes
        int newNode = searchGraph.mergeNodes(cycleNodesSet);

        for (const auto& cycleNode : cycleNodesSet) {
            for (const auto& pair : nodeToPredecessor[cycleNode]) {
                int neighbour = pair.first;
                nodeToPredecessor[neighbour].erase(cycleNode);
                if (createComponent) {
                    nodeToPredecessor[neighbour][newNode] = 0;
                    nodeToPredecessor[newNode][neighbour] = 0;
                };
            };
            nodeToPredecessor.erase(cycleNode);
        };

        // insert node remap here if required

        handleSelfEdges();

        if (createComponent) {
            nonCycleNodesSet.insert(newNode);
            int newComponentId = getNewComponentId();
            components[newComponentId] = nonCycleNodesSet;
            for (const auto& node : nonCycleNodesSet) {
                nodeToComponent[node] = newComponentId;
            };
            updateComponentCost(newComponentId);
        };
    };

    void initialSetup() {
        bool reset = true;

        while (reset) {
            reset = false;

            handleSelfEdges();

            // iterate over all nodes initially
            for (int nodeId : searchGraph.getAllNodeIds()) {
                if (reset) break;

                // ignore node if already in a component
                auto component = nodeToComponent.find(nodeId);
                if (component != nodeToComponent.end()) {
                    continue;
                };

                py::print("creating new component for node ", nodeId);

                // create new component
                std::set<int> newComponent;
                newComponent.insert(nodeId);
                int newComponentId = getNewComponentId();
                components[newComponentId] = newComponent;
                nodeToComponent[nodeId] = newComponentId;

                // add all nodes to component that have negative cost
                std::map<int, int> previousSearchedNodes;
                int previousSearchedNode;
                std::vector<int> unsearchedNodes;
                unsearchedNodes.push_back(nodeId);
                while (!unsearchedNodes.empty()) {
                    if (reset) break;
                    int unsearchedNode = unsearchedNodes.back();
                    py::print("searching node ", unsearchedNode);
                    unsearchedNodes.pop_back();

                    auto it = previousSearchedNodes.find(unsearchedNode);
                    if (it != previousSearchedNodes.end()) {
                        previousSearchedNode = previousSearchedNodes[unsearchedNode];
                    };

                    for (const Edge& edge : searchGraph.getEdges(unsearchedNode)) {
                        int newNode = edge.node2;
                        if (it != previousSearchedNodes.end() && previousSearchedNode == newNode) continue;

                        if (edge.cost == -1) {
                            // check for cycle
                            // --------------------------------------------------------------------
                            if (newComponent.contains(newNode)) {
                                py::print("found cycle for nodes ", newNode, " and ", unsearchedNode, " in component ", newComponentId);

                                // cycle found
                                auto [path, cost] = findPath(newNode, unsearchedNode);

                                // add last node and edge to make the path to a cycle
                                cost += edge.cost;
                                path.push_back({ unsearchedNode, edge });

                                handleCycle(path, false);

                                reset = true;
                                break;
                            }

                            py::print("adding node ", newNode, " to component ", newComponentId);

                            previousSearchedNodes[newNode] = unsearchedNode;

                            nodeToPredecessor[newNode][unsearchedNode] = 0;
                            nodeToPredecessor[unsearchedNode][newNode] = 0;

                            // add node to component
                            newComponent.insert(edge.node2);
                            components[newComponentId] = newComponent;
                            unsearchedNodes.push_back(edge.node2);
                            nodeToComponent[edge.node2] = newComponentId;

                            // update costs
                            updateComponentCost(newComponentId);
                        };
                    };
                };
            };
        };
    };

    void mergeComponents(int swallower, int swallowee) {
        py::print("merging component ", swallowee, " into component ", swallower);
        if (swallower == swallowee) {
            throw std::runtime_error("Merging a component into itself is not possible.");
        };

        std::set_union(components[swallower].begin(), components[swallower].end(), components[swallowee].begin(), components[swallowee].end(), std::inserter(components[swallower], components[swallower].begin()));

        for (const auto& node : components[swallowee]) {
            nodeToComponent[node] = swallower;
        };

        components.erase(swallowee);
    };

    bool searchFrom(int startNode) {
        int startComponentId = nodeToComponent[startNode];

        py::print("searching from", startNode, "of component", startComponentId);

        std::map<int, std::tuple<int, int>> foundNodes;
        foundNodes[startNode] = { startNode, 0 };
        std::set<std::tuple<int, int, int>, TupleComparator> nodeQueue;
        int iterNode;
        int iterPredecessor;

        for (const auto& pair : searchGraph.getEdges(startNode)) {
            int neighbor = pair.node2;
            py::print("neighbor:", neighbor, "of component", nodeToComponent[neighbor]);
            // difference to python implementation
            // check if neigbor is in node to predecessor
            auto it = nodeToPredecessor[startNode].find(neighbor);
            if (it == nodeToPredecessor[startNode].end()) {
                int neighborCost = searchGraph.getMinCostEdge(startNode, neighbor).cost;
                nodeQueue.emplace(neighbor, startNode, neighborCost);
                py::print("added to node queue");
            };
        };

        py::print(startNode, "has", nodeQueue.size(), "neighbors");

        while (!nodeQueue.empty()) {
            auto firstElement = *nodeQueue.begin();
            auto [node, predecessor, cost] = firstElement;
            py::print("step: ", node, predecessor, cost);
            nodeQueue.erase(firstElement);

            foundNodes[node] = { predecessor, cost };

            int lowestPathCost = std::get<1>(getLowestCostPredecessor(node));
            py::print("lowest path cost:", lowestPathCost);
            if (lowestPathCost < 0 && node != startNode) {
                int componentId = nodeToComponent[node];
                py::print("component id:", componentId, "start component id:", startComponentId);
                if (componentId == startComponentId) {
                    py::print("found cycle for nodes ", startNode, " and ", node, " in component ", componentId);
                    // found cycle
                    // find path through component and add to cycle
                    auto [path, pathCost] = findPath(startNode, node);

                    if (pathCost + cost >= 0) continue;

                    // find newly found path through positive edges and add to cycle
                    iterNode = node;
                    iterPredecessor = predecessor;
                    while (iterNode != startNode) {
                        Edge edge = searchGraph.getMinCostEdge(iterNode, iterPredecessor);
                        path.emplace_back(iterNode, edge);
                        iterNode = iterPredecessor;
                        iterPredecessor = std::get<0>(foundNodes[iterPredecessor]);
                    };
                    handleCycle(path);
                    return true;
                };

                // merge components and all nodes inbetween

                // update node_to_predecessor to prepare for merging
                iterNode = node;
                iterPredecessor = predecessor;
                while (iterNode != startNode) {
                    nodeToPredecessor[iterNode][iterPredecessor] = 0;
                    nodeToPredecessor[iterPredecessor][iterNode] = 0;
                    if (startComponentId != nodeToComponent[iterNode]) {
                        mergeComponents(startComponentId, nodeToComponent[iterNode]);
                    }

                    iterNode = iterPredecessor;
                    iterPredecessor = std::get<0>(foundNodes[iterPredecessor]);
                };
                updateComponentCost(startComponentId);
                return true;
                // extension here
            };

            py::print("cost:", cost);

            // add next nodes to node queue and calculate cost
            for (const auto& edge : searchGraph.getEdges(node)) {
                int neighbor = edge.node2;
                if (neighbor != predecessor && neighbor != node) {
                    int neighborCost = cost + searchGraph.getMinCostEdge(neighbor, node).cost;
                    if (foundNodes.contains(neighbor)) {
                        py::print("neighbor", neighbor, "was found before");
                        if (std::get<1>(foundNodes[neighbor]) > neighborCost) {
                            py::print(std::get<1>(foundNodes[neighbor]), ">", neighborCost);
                            foundNodes[neighbor] = { node, neighborCost };
                        } else {
                            py::print(std::get<1>(foundNodes[neighbor]), "<=", neighborCost);
                            continue;
                        };
                    };
                    nodeQueue.emplace(neighbor, node, neighborCost);
                };
            };
        };

        return false;
    };

    void search() {
        std::set<int> ignoreNodes;
        bool repeat = true;
        while (repeat) {
            int minCost = 100;
            int minNode;
            repeat = false;
            for (const auto& node : searchGraph.getAllNodeIds()) {
                if (ignoreNodes.contains(node)) {
                    py::print(node, "was ignored");
                    continue;
                } else {
                    py::print(node, "was not ignored");
                };

                int cost = std::get<1>(getLowestCostPredecessor(node));
                if (cost < minCost) {
                    minCost = cost;
                    minNode = node;
                };
            };

            handleSelfEdges();
            if (!searchFrom(minNode)) {
                py::print(minNode, "will be ignored");
                ignoreNodes.insert(minNode);
            } else {
                ignoreNodes.clear();
                repeat = true;
            };
        };
    };

    std::set<int> solve() {
        py::print("starting initial setup");
        initialSetup();
        py::print("finished initial setup, starting search");
        search();
        py::print("finished search");

        return multicut;
    };
};

Solver getSolver() {
    return Solver();
};

/*
int main() {
    // Create a graph
    Graph g;

    // Add edges with weights
    g.addEdge(0, 1, 1, 3, 1);
    g.addEdge(0, 2, 1, 5, 2);
    g.addEdge(1, 2, 1, 2, 3);
    g.addEdge(1, 3, 1, 7, 4);
    g.addEdge(0, 1, 2, 2, 5);
    g.addEdge(1, 0, 3, 3, 6);


    // Print the graph with colors
    std::cout << "Finished\n";

    return 0;
}
*/

PYBIND11_MODULE(spm_solver, m) {
    m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------

        .. currentmodule:: spm_solver

        .. autosummary::
           :toctree: _generate

           add
           subtract
    )pbdoc";
    
    pybind11::class_<Solver>(m, "Solver")
        .def(pybind11::init<>())
        .def("load_graph", &Solver::loadGraph)
        .def("load_search_graph", &Solver::loadSearchGraph)
        .def("solve", &Solver::solve);

    m.def("get_solver", &getSolver, R"pbdoc(
        Creates a Solver which handles solving the multicut problem.
    )pbdoc");

}
