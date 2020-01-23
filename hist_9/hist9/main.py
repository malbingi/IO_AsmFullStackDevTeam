import matplotlib.pyplot as plt
import git
import networkx as nx


def main():
    def getVer():
        try:
            repo = git.Repo('../../')
            sha = repo.head.object.hexsha
        except:
            sha = 'unknown'
        return sha

    plt.title("Version: " + getVer())
    G = nx.DiGraph()
    pos = nx.spring_layout(G)
    nx.draw(G, pos, edge_color='black', width=1, node_size=1000, node_color='#fff989', with_labels=True)
    edge_labels = dict([((u, v,), d['length']) for u, v, d in G.edges(data=True)])
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.2)
    plt.show()


if __name__ == "__main__":
    main()
