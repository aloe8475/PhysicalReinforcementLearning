"Created on Thu Jul  1 13:16:32 2021 "
" @author: gnate "
# Define some noise functions
import numpy as np
import pandas as pd
#Append path to Ruomin's Edamame Package (Nanowire Simulations)
import sys
sys.path.append('/import/silo2/aloe8475/Documents/edamame')
from edamame import * 

# -------------------------------
# Data Creation/Loading Functions 
# -------------------------------

def zero_bit_noise(N):
    noise_list = []
    noise_vec = np.zeros((1,N))
    noise_list.append(noise_vec)
    return noise_list

def one_bit_noise(N):
    noise_list = []
    for i in range(0,N):
        noise_vec = np.zeros((1,N))
        noise_vec[0,i] = 1
        noise_list.append(noise_vec)
    return noise_list

def xor_array(x,y,N):
    a = x.reshape((1,N))
    b = y.reshape((1,N))
    output_vec = np.zeros((1,a.shape[1]), dtype = 'uint')
    for i in range(0, a.shape[1]):
        output_vec[0, i] = a[0, i] ^ b[0, i]
    return output_vec     

def hamming_dist(x,y,N):
    dist = 0
    output_vec = xor_array(x,y,N)
    dist = sum(output_vec.T)
    return dist
  
def generate_data(N):
    if N == 9:
        orig_inputs = ['111010111', '101010010', '101111101']
    elif N == 25:
        orig_inputs = ['1111100010001000100011111', '1000101010010100010000100', '1000111001101011001110001'] #z v n in 5x5
       
    orig_inputs_matrix = np.zeros((len(orig_inputs), 1, N), dtype = 'uint')
    for i in range(0,len(orig_inputs)):
        input_tuple = tuple(orig_inputs[i])
        for j in range(0, N):
            if input_tuple[j] == '1': orig_inputs_matrix[i,0,j] = 1
    # Generate 5x5 noisy data
    noise_vectors = []
    noise_vectors.append(zero_bit_noise(N))
    noise_vectors.append(one_bit_noise(N))
    #print('Noise vectors - ', noise_vectors)
    count_vec = np.zeros(2, dtype = 'uint')
    for i in range(0,2):
        count_vec[i] = np.math.factorial(N)/(np.math.factorial(i)*np.math.factorial(N-i))

    noisy_data_matrix = np.zeros((len(orig_inputs)*int(sum(count_vec)), 1, N), dtype = 'uint')
    row_count = 0
    for i in range(0,len(orig_inputs)):
        for j in range(0,2):
            bit_noise = np.array(noise_vectors[j], dtype = 'uint')
            for k in range(0, int(count_vec[j])):
                noisy_data_matrix[row_count] = xor_array(orig_inputs_matrix[i], bit_noise[k],N)
                row_count += 1

    final_data_matrix = np.zeros((len(orig_inputs)*int(sum(count_vec)), 1, N+1), dtype = 'uint')
    final_data_matrix[0:len(orig_inputs)*int(sum(count_vec)), 0, 0:N] = noisy_data_matrix.reshape(len(orig_inputs)*int(sum(count_vec)), N)

    for i in range(0,len(orig_inputs)):
        final_data_matrix[int(sum(count_vec))*i: int(sum(count_vec))*(i+1), 0, N] = i
    if N == 9:
        np.savetxt("3x3image_gen.csv", final_data_matrix.reshape(len(orig_inputs)*int(sum(count_vec)), N+1), delimiter=",")	
    elif N == 25:
        np.savetxt("5x5image_gen.csv", final_data_matrix.reshape(len(orig_inputs)*int(sum(count_vec)), N+1), delimiter=",")
	
 
def create_target(t):
    target_vector=np.zeros([t.shape[0],3])
    for row in range(t.shape[0]):
        target_vector[row,:] = np.zeros(3)
        for i in range(3):
            if i == t[row]:
                 target_vector[row,i] = 1    
    return target_vector
 
def create_single_target(t):
        target_vector = np.zeros(3)
        for i in range(3):
            if i == t:
                target_vector[i] = 1
        return target_vector

# Define angle function for rotating plot gif    
# def rotate(angle):
#        ax.view_init(azim=angle)"

# Load 3x3 dataset
def load_data(N):
    if N == 9:
        letters = pd.read_csv("./3x3image_gen.csv", sep=',', header = None)
        sample_num = 30      # Number of data samples
    elif N == 25:
        letters = pd.read_csv("./5x5image_gen.csv", sep=',', header = None)
        sample_num = len(letters)      # Number of data samples

    data = letters.values[:, 0:N]
    
    # Target labels: 0 - 'z', 1 - 'v', 2 - 'n
    targets = letters.values[:, N]
    inputs = np.zeros((sample_num,N+1))
    inputs[:,0:N] = data
    inputs[:,N] = np.ones(sample_num)   #Bias input
    
    # One-hot encoding of outputs
    onehot_outputs = create_target(targets) #1 0 0 = z, 0 1 0 = v, 0 0 1 = n
    
    # Standardize data - Uncomment to standardize data, not necessary
    # inputs = data - np.mean(data)
	# inputs = inputs/(np.std(data))"
    return inputs, onehot_outputs, sample_num, targets
    
# ------------------------------
# Equilibrium/Backprop Functions 
# ------------------------------

#Calculate cost function
def calc_cost(x,y):
    return (1/2)*((x-y)**2) #we need to account for the fact where some non-target drains will have -ve current that impacts the +ve current drains
 
#Training + Testing Functions:

def setupStimulus(training_stimulus,currInput,run_time=2,onAmp=1,signalType='DC'):
    #This function sets up the stimuli for simulations. 
    for i in range(num_drain_training):
        training_stimulus.append((stimulus__(biasType='Drain',T=run_time,dt=dt)))
        
    #Sources
    for i in range(len(currInput)):
        if currInput[i]>0:
            training_stimulus.append((stimulus__(biasType=signalType,onAmp=onAmp*currInput[i],T=run_time,dt=dt)))
    #         else: #non-active sources are changed to 0.005 instead of 0, to reduce sink behaviour between sources
    #             training_stimulus.append((stimulus__(biasType=signalType,onAmp=0.01,T=run_time,dt=dt)))
    return training_stimulus

def setupSourcesOnly(stim,currInput,onAmp=1,run_time=2,signalType='DC'):
    #This function sets up the stimuli for the testing part of the simulation. 
    #Sources
    stimulus=copy.deepcopy(stim)
    for i in range(len(currInput)):
        if currInput[i]>0:
            stimulus.append((stimulus__(biasType=signalType,onAmp=onAmp*currInput[i],T=run_time,dt=dt)))
    #         else:
    #             stimulus.append((stimulus__(biasType=signalType,onAmp=0.01,T=run_time,dt=dt)))
    return stimulus

def runTesting(outputVals,th,th2):
    n     = len(outputVals)   
    cost=calc_cost(outputVals,target_values) 
    return cost

def getNWState(training_stimulus,connectivity,state,drain_pool,sources,dt=0.01,run_time=2):
    #This function runs each training epoch and saves the network state at the last timestep of that epoch
    eles = np.append(drain_pool, sources) #all drains
    #     if len(eles) == num_drain_training + num_source_training:
    training_sim = runSim(connectivity, stimulus = training_stimulus,
                       junctionMode = 'tunneling',
                       dt = dt, T = run_time, 
                       contactMode = 'preSet',
                       electrodes = eles,
                       findFirst = False,
                       start_state = state,
                       disable_tqdm=False,
                       criticalFlux=0.1)  
    JS1 = getJunctionState(training_sim, -1) #save state
    #     else: 
    #         print('Bless you Joel :)')
    return training_sim,JS1


def calcOutputs(sim2, sources,all_drains):
    #This function calculates the current and voltage read out at each drain electrode, 
    #which we use to determine if the target threshold for each electrode is met
    
    cc = [None]*len(all_drains)#np.zeros(len(all_drains))
    volt = [None]*len(all_drains)#np.zeros(len(all_drains))

    # ALTERNATIVE METHOD SUGGESTED BY JOEL

    #Index network state:
        #IF PULSE - we want the state of the network at the end of the last pulse 
    #     if sim2.stimulus[-1].biasType=='Pulse':
    #         t=sim2.stimulus[-1].signal>0.005
    #         idx=[i for i, x in enumerate(t) if x][-1]
    #     else: #otherwise we take 4 timesteps as the state of the network 
    #         idx=[500,1000,1500,-1]
    #         idx=-1
            
        
    #Calculate Current at network state: 
    for i, d in enumerate(all_drains): #for each drain electrode
        #current
        cc[i]=sim2.electrodeCurrent.T[i]#[idx]#/(sim2.wireVoltage.T[sources[0]][idx]-sim2.wireVoltage.T[d][idx])
        #voltage
        volt[i]=sim2.wireVoltage.T[d]#[idx]#/sim2.electrodeCurrent.T[i][idx]
       
        # Conductance = Current Drain / (Voltage Source - Voltage Drain)
    return cc


# ------------------------
# Miscellaneous  Functions
# ------------------------

#Generating Electrode positions in Network - Written by Ruomin Zhu
def genGridNW(xa,xb,ya,yb,ex,ey):
  e = []
  for i in range(len(ex)):
      d = np.zeros(len(xa))
      for j in range(len(xa)):
          d[j]=dist((xa[j], ya[j]), (xb[j], yb[j]), (ex[i], ey[i]))
      e.append(np.argmin(d))
  return np.array(e)

def point_on_line(a, b, p):
  ap = p - a
  ab = b - a
  result = a + np.dot(ap, ab) / np.dot(ab, ab) * ab
  return result

def dist(p1,p2,p3):
  p1=np.array(p1) #xa ya
  p2=np.array(p2) #xb yb
  p3=np.array(p3) # ex ey (electrode placement)
  
  #determine whether closest point to electrode is on the line, or outside the line 
  t=point_on_line(p1,p2,p3)
  if t[1]<p1[1]:
      r = np.linalg.norm(p3-p1) #if point is outside left (xvalues)
  elif t[1] > p2[1]:
      r = np.linalg.norm(p3-p2) #if point is outside right (xvalues)
  else:
      r = np.linalg.norm(np.cross(p2-p1, p1-p3))/np.linalg.norm(p2-p1) #if point is inside xvalues
  return r
      
      
#VISUALISE NETWORK STATE
def getWeightedGraph(edgeList,numWires,nwState):#, this_TimeStamp = 0):
#     edgeList = network['edge_list'],
    adjMat = np.zeros((numWires, numWires))
#     set_trace(),
    adjMat[edgeList[:,0], edgeList[:,1]] = nwState.voltage*nwState.conductance#network.junctionSwitch[this_TimeStamp,:] #CHANGE THIS TO CONDUCTANCE THRESHOLD?
    adjMat[edgeList[:,1], edgeList[:,0]] = nwState.voltage*nwState.conductance#network.junctionSwitch[this_TimeStamp,:] #CHANGE THIS TO CONDUCTANCE THRESHOLD?
    WeightedGraph = nx.from_numpy_array(adjMat)
    WeightedGraph=nx.DiGraph.to_undirected(WeightedGraph)
    
    return WeightedGraph

def draw_network_state(connectivity,nwState):
    adjMat=connectivity.adj_matrix
    graph=nx.from_numpy_array(adjMat)
    OGgraph=graph.copy()
    pos=nx.kamada_kawai_layout(OGgraph)
    numWires=graph.number_of_nodes()
    edgeList=np.array(list(graph.edges()))
    weightedSubGraph=getWeightedGraph(edgeList,numWires,nwState)
    minWeights=-1e-5 #currents
    maxWeights=1e-5 #currents
    
    #draw network
    #%matplotlib inline
    f,ax=plt.subplots(figsize=(10,6))
    G=weightedSubGraph
    edge_weights=nx.get_edge_attributes(G,'weight')
#     G.remove_edges_from((e for e, w in edge_weights.items() if w <1e-5)) ,
    edges=G.edges()
    weights=[G[u][v]['weight'] for u,v in edges]
    
    #draw OG graph,
    pos=nx.kamada_kawai_layout(OGgraph)
    h=nx.draw_networkx_nodes(OGgraph,pos=pos,node_color='grey',node_size=10,ax=ax)
    h.set_zorder(1),
    
    h2=nx.draw_networkx_edges(G,pos=pos,ax=ax,edge_color=weights,edge_cmap=plt.cm.bwr,edge_vmin=minWeights,edge_vmax=maxWeights)
#     if h2:,
#         h2.set_norm(clrs.SymLogNorm(10)),
#         h2.set_zorder(3),
    #             if j == 10 and i == 6:,
    #                 plt.colorbar(h2),
    nx.draw_networkx_nodes(G,pos=pos,nodelist=sources,node_color='#3f9b0b',node_size=120,node_shape ='*',ax=ax)
    nx.draw_networkx_nodes(G,pos=pos,nodelist=drain_pool,node_color='r',node_size=120,node_shape ='*',ax=ax)
    plt.colorbar(h2,label='current',ax=ax)
    plt.show()



