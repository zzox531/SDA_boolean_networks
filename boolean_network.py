import networkx as nx
import boolean as bool
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random


class BN():

    __bool_algebra = bool.BooleanAlgebra()


    """
    Helper method for converting a non-negative integer into a state in the form of a tuple of 0s and 1s.

        Args:
            x (int): A state number

        Returns:
            tuple[int, ...]: A tuple of 0s and 1s representing the Boolean network state.
    """
    def int_to_state(self, x: int) -> tuple[int, ...]:

        binary_str = format(x,'0'+str(self.num_nodes)+'b')
        state = [int(char) for char in binary_str]

        return tuple(state)


    """
    Converts a Boolean network state from a tuple of 0s and 1s into a binary string.

        Args:
            state (tuple[int, ...]): A tuple of 0s and 1s representing the Boolean network state

        Returns:
            str: A binary string representing the Boolean network state
    """
    @staticmethod
    def state_to_binary_str(state: tuple[int, ...]) -> str:
        bin_str = ''
        for bit in state:
            bin_str += str(bit)
        
        return bin_str


    """
    Class constructor

        Args:
            list_of_nodes (list[str]): A list of node names

            list_of_functions (list[str]): A list of strings representing the Boolean functions for the corresponding nodes
                in the list_of_nodes, e.g. '(x0 & ~x1) | x2', where 'x0', 'x1', and 'x2' are node names.
        
    """
    def __init__(
        self, 
        list_of_nodes: list[str], 
        list_of_functions: list[str], 
        attrs_async: set[tuple[int, ...]] = None, 
        attrs_sync: set[tuple[int, ...]] = None,
        parents_async: dict[tuple[int, ...], list[tuple[int, ...]]] = None,
        parents_sync: dict[tuple[int, ...], list[tuple[int, ...]]] = None
    ):
        
        self.num_nodes = len(list_of_nodes)

        self.node_names = list_of_nodes
        self.functions_str = list_of_functions
        
        self.list_of_nodes = []
        for node_name in list_of_nodes:
            node = self.__bool_algebra.Symbol(node_name)
            self.list_of_nodes.append(node)
        
        self.functions = []
        for fun in list_of_functions:
            self.functions.append(self.__bool_algebra.parse(fun,simplify=True))

        if attrs_async is not None:
            self.attractor_set_async = attrs_async
        else:
            attractors_async = self.get_attractors_async()
            self.attractor_set_async = set()
            for attr in attractors_async:
                for state in attr:
                    self.attractor_set_async.add(state)            
                
        if attrs_sync is not None:
            self.attractor_set_sync = attrs_sync
        else:
            self.attractor_set_sync = self.get_attractors_sync()
                
        if parents_async is not None:
            self.parents_async = parents_async
        else:
            self.parents_async = {}

        if parents_sync is not None:
            self.parents_sync = parents_sync
        else:
            self.parents_sync = {}
            
        if parents_async is None or parents_sync is None:
            for i in range(2**self.num_nodes):
                tpl = []
                for j in range(self.num_nodes):
                    if 2**j & i != 0:
                        tpl.append(1)
                    else:
                        tpl.append(0)
                tpl = tpl[::-1]
                tpl = tuple(tpl)
                
                # Sync parents
                if parents_sync is None:
                    neighbor_sync = self.get_neighbor_state_sync(tpl)
                    if neighbor_sync in self.parents_sync:
                        self.parents_sync[neighbor_sync].append(tpl)
                    else:
                        self.parents_sync[neighbor_sync] = [tpl]
                    
                # Async parents
                if parents_async is None:
                    neighbors_async = self.get_neighbor_states_async(tpl)
                    for state in neighbors_async:
                        if state in self.parents_async:
                            self.parents_async[state].append(tpl)
                        else:
                            self.parents_async[state] = [tpl]
                              
    def sample_parent_state_sync(self, state: tuple[int, ...]) -> set[tuple[int, ...]]:
        
        if state not in self.parents_sync:
            return None
        return random.choice(self.parents_sync[state])

    def sample_parent_state_async(self, state: tuple[int, ...]) -> set[tuple[int, ...]]:
        if state not in self.parents_async:
            return None
        return random.choice(self.parents_async[state])
        

    """
    Computes the states reachable from the given state in one step of asynchronous update.

        Args:
            state (tuple[int, ...]): A tuple of 0s and 1s representing the Boolean network state.

        Returns:
            set[tuple[int, ...]]: A set of tuples of 0s and 1s representing the Boolean network states reachable
                in one step from the given state.
    """
    def get_neighbor_states_async(self, state: tuple[int, ...]) -> set[tuple[int, ...]]:
        kwargs = {}
        for i in range(self.num_nodes):
            kwargs[self.node_names[i]] = state[i]
        
        neighbor_states = set()

        for i, func in enumerate(self.functions):
            # Check if the function is TRUE / FALSE, it then doesn't need to be called
            if (func == self.__bool_algebra.TRUE):
                new_value = 1
            elif(func == self.__bool_algebra.FALSE):
                new_value = 0
            else:
                new_value = int(func(**kwargs))
            new_tuple = list(state)
            new_tuple[i] = new_value
            neighbor_states.add(tuple(new_tuple))

        return neighbor_states

    """
    Computes the states reachable from the given state in one step of synchronous update.

        Args:
            state (tuple[int, ...]): A tuple of 0s and 1s representing the Boolean network state.

        Returns:
            set[tuple[int, ...]]: A set of tuples of 0s and 1s representing the Boolean network states reachable
                in one step from the given state.
    """
    def get_neighbor_state_sync(self, state: tuple[int, ...]) -> tuple[int, ...]:
        kwargs = {}
        for i in range(self.num_nodes):
            kwargs[self.node_names[i]] = state[i]
        
        new_tuple = list(state)

        for i, func in enumerate(self.functions):
            # Check if the function is TRUE / FALSE, it then doesn't need to be called
            if (func == self.__bool_algebra.TRUE):
                new_value = 1
            elif(func == self.__bool_algebra.FALSE):
                new_value = 0
            else:
                new_value = int(func(**kwargs))
            new_tuple[i] = new_value

        return tuple(new_tuple)
    
    """
    Generates the asynchronous state transition system of the Boolean network.

        Returns:
            nx.DiGraph: NetworkX DiGraph object representing the asynchronous state transition system.

    """
    def generate_state_transition_system(self) -> nx.DiGraph:
        
        G = nx.DiGraph()
        G.add_nodes_from([self.int_to_state(i) for i in range(2**self.num_nodes)])
        
        for state_num in range(2**self.num_nodes):
            state = self.int_to_state(state_num)
            neighbor_states = self.get_neighbor_states_async(state)
            for neighbor in neighbor_states:
                G.add_edge(state, neighbor)

        return G


    """
    Computes the asynchronous attractors of the Boolean network.

        Returns:
            list[set[tuple[int]]]: A list of asynchronous attractors. Each attractor is a set of states.
    """
    def get_attractors_async(self) -> list[set[tuple[int]]]:
        sts = self.generate_state_transition_system()

        attractors = []
        for attractor in nx.attracting_components(sts):
            attractors.append(attractor)

        return attractors
    
    """
    Computes the synchronous attractors of the Boolean network.
    
        Returns:
            set[tuple[int]]: A set of all states within synchronous attractors.    
    """
    def get_attractors_sync(self) -> set[tuple[int]]:
        attractor_states = set()
        for i in range(2**self.num_nodes):
            state = self.int_to_state(i)
            visited = {}
            current_state = state
            while current_state not in visited:
                visited[current_state] = True
                current_state = self.get_neighbor_state_sync(current_state)
            # We've found a cycle, extract it
            if current_state in attractor_states:
                continue
            cycle_start_state = current_state
            attractor_states.add(current_state)
            current_state = self.get_neighbor_state_sync(cycle_start_state)
            while current_state != cycle_start_state:
                attractor_states.add(current_state)
                current_state = self.get_neighbor_state_sync(current_state)
        return attractor_states
        
            
    
    """
    Computes wether a state is within any attractor of the Boolean network.
    
        Args:
            state (tuple[int, ...]): A tuple of 0s and 1s representing the Boolean network state.
            synchronous (bool, optional): Whether to check for synchronous attractor. Defaults to True.

        Returns:
            bool: True / False wether the state is an attractor.
    """
    def is_attractor(self, state: tuple[int, ...], synchronous: bool = True) -> bool:
        if synchronous:
            if state in self.attractor_set_sync:
                return True
        else:
            if state in self.attractor_set_async:
                return True
        return False
    
    """
    Draws the state transition system.

        Args:
            highlight_attractors: If True, states belonging to different attractors are drawn 
                using distinct colors.

        Returns:
            None
    """
    def draw_state_transition_system(self, path: str, highlight_attractors: bool = True) -> None:

        # The color used for non-attractor states in the state transition system
        NON_ATTRACTOR_STATE_COLOR = 'grey'

        sts = self.generate_state_transition_system()

        if highlight_attractors:
            attractors = self.get_attractors_async()

            sts_nodes = list(sts.nodes)

            node_colors = [NON_ATTRACTOR_STATE_COLOR for node in sts_nodes]

            colors = list(mcolors.CSS4_COLORS)
            colors.remove('white')
            colors.remove(NON_ATTRACTOR_STATE_COLOR)
            
            for attractor in attractors:
                # Select a random color for coloring the states of the attractor
                color = random.choice(colors)
                for state in attractor:
                    node_colors[sts_nodes.index(state)] = color

        # Draw the graph. Different layouts can be used, for a full list see
        # https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout
        # 
        # A better drawing can be obtained with the PyGraphviz.AGraph class, but requires the installation of
        # PyGraphviz (https://pygraphviz.github.io/)
        nx.draw_networkx(sts,
                         with_labels=True,
                         pos=nx.spring_layout(sts, k=3.0, iterations=200, seed=42),
                         node_color = node_colors,
                         font_size=8)

        plt.savefig(path, dpi=1000, bbox_inches="tight")
        plt.close()

