'''
test filter experiments
'''

# import self-defined modules
import sys
sys.path.append('/Users/cynthia/Desktop/Capstone-CodeAnalysis/CodeAnalysis')
from evaluation.utils import api_request

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm  

load_dotenv()
API_KEY = os.getenv('API_KEY')
ORGANIZATION = os.getenv('ORGANIZATION')
CLIENT = OpenAI(api_key=API_KEY, organization=ORGANIZATION)


def process_file(file_folder, exact_file, metadata_type='celltype'):
    full_path = os.path.join(file_folder, exact_file)
    with open(full_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        file_content = file_content[:5000]  #128,000 token
    if metadata_type=='celltype':
        prompt = (
        f"You are a neuroscience expert specializing in cell types analysis. "
        f"Given the following content:\n\n{file_content}\n\n"
        f"Please identify the most relevant cell types from the following list. "
        f"The list includes: ['Dentate gyrus granule GLU cell', 'Hippocampus CA1 pyramidal GLU cell', 'Hippocampus CA3 pyramidal GLU cell', "
        f"'Neostriatum medium spiny direct pathway GABA cell', 'Substantia nigra pars compacta DA cell', "
        f"'Thalamus geniculate nucleus/lateral principal GLU cell', 'Thalamus reticular nucleus GABA cell', "
        f"'Neocortex L5/6 pyramidal GLU cell', 'Neocortex L2/3 pyramidal GLU cell', 'Olfactory bulb main mitral GLU cell', "
        f"'Olfactory receptor GLU cell', 'Piriform cortex anterior pyramidal layer II GLU cell', 'Retina ganglion GLU cell', "
        f"'Cerebellum Purkinje GABA cell', 'Vestibular organ hair GLU cell', 'Cochlear nucleus bushy GLU cell', "
        f"'Cochlear nucleus pyramidal/fusiform GLU cell', 'Spinal cord lumbar Interneuron 1a GLY cell', "
        f"'Spinal cord lumbar motor neuron alpha ACh cell', 'Cochlear nucleus octopus GLU cell', 'Cochlea hair outer GLU cell', "
        f"'Retina photoreceptor cone GLU cell', 'Antennal lobe olfactory projection neuron (insect)', "
        f"'Olfactory bulb main interneuron periglomerular GABA cell', 'Olfactory bulb main interneuron granule MC GABA cell', "
        f"'Piriform cortex anterior interneuron superficial GABA cell', 'Piriform cortex anterior interneuron deep layer GABA cell', "
        f"'Retina bipolar GLU cell', 'Neostriatum interneuron ACh cell', 'Cerebellum interneuron granule GLU cell', "
        f"'Neocortex V1 interneuron basket PV GABA cell', 'Hippocampus CA1 interneuron oriens alveus GABA cell', "
        f"'Olfactory bulb main tufted middle GLU cell', 'Olfactory bulb main interneuron granule TC GABA cell', "
        f"'Neostriatum medium spiny indirect pathway GABA cell', 'Retina photoreceptor rod GLU cell', "
        f"'Hippocampus CA3 interneuron basket GABA cell', 'Neocortex U1 L5B pyramidal pyramidal tract GLU cell', "
        f"'Neocortex U1 L2/6 pyramidal intratelencephalic GLU cell', 'Neocortex U1 L6 pyramidal corticalthalamic GLU cell', "
        f"'Substantia nigra pars reticulata principal GABA cell', 'Globus pallidus principal GABA cell', "
        f"'Neostriatum interneuron gaba/parvalbumin GABA cell', 'Neostriatum interneuron SOM/NOS GABA cell', "
        f"'Subthalamic nucleus principal GABA cell', 'Hippocampus CA4 pyramidal GLU cell', 'Hippocampus CA1 interneuron basket GABA cell', "
        f"'Locus ceruleus principal NE cell', 'Raphe nuclei principal 5HT cell', 'Septum principal ACh cell', "
        f"'Neocortex M1 L2/6 pyramidal intratelencephalic GLU cell', 'Neocortex M1 L6 pyramidal corticothalamic GLU cell', "
        f"'Neocortex M1 L5B pyramidal pyramidal tract GLU cell', 'Neocortex V1 L5B pyramidal pyramidal tract GLU cell', "
        f"'Neocortex V1 interneuron bipolar VIP/CR GABA cell', 'Neocortex V1 interneuron chandelier SOM GABA cell', "
        f"'Neocortex V1 L4 stellate GLU cell', 'Neocortex M1 interneuron basket PV GABA cell', 'Neocortex U1 interneuron basket PV GABA cell', "
        f"'Neocortex M1 L4 stellate GLU cell', 'Neocortex U1 L4 stellate GLU cell', 'Neocortex M1 interneuron bipolar VIP/CR GABA cell', "
        f"'Neocortex U1 interneuron bipolar VIP/CR GABA cell', 'Neocortex M1 interneuron chandelier SOM GABA cell', "
        f"'Neocortex U1 interneuron chandelier SOM GABA cell', 'Cochlea hair inner GLU cell', 'Spinal cord lumbar motor neuron gamma ACh cell', "
        f"'Retina horizontal GABA cell', 'Retina amacrine ACh cell', 'Hippocampus CA3 interneuron oriens alveus GABA cell', "
        f"'Cerebellum interneuron Golgi GABA cell', 'Cerebellum interneuron stellate GABA cell', 'Olfactory bulb main interneuron tufted external GABA cell', "
        f"'Olfactory bulb short axon deep GABA cell', 'Piriform cortex anterior semilunar GLU cell', 'Piriform cortex anterior pyramidal deep GLU cell', "
        f"'Piriform cortex anterior interneuron layer II GABA cell', 'Piriform cortex posterior semilunar GLU cell', "
        f"'Piriform cortex posterior pyramidal layer II GLU cell', 'Piriform cortex posterior pyramidal deep GLU cell', "
        f"'Piriform cortex posterior interneuron superficial GABA cell', 'Piriform cortex posterior interneuron layer ll GABA cell', "
        f"'Piriform cortex posterior interneuron deep GABA cell', 'Myelinated neuron', 'Neocortex spiny stellate cell', "
        f"'Nucleus laminaris neuron', 'Medial Nucleus of the Trapezoid Body (MNTB) neuron', 'Skeletal muscle cell', "
        f"'Stomatogastric Ganglion (STG) Modulatory commissural neuron 1 (MCN1)', 'Stomatogastric Ganglion (STG) interneuron 1 (Int1)', "
        f"'Stomatogastric Ganglion (STG) Lateral Gastric (LG) cell', 'Arteriolar network', 'Cardiac atrial cell', 'Heart cell', "
        f"'Dentate gyrus basket cell', 'Leech pressure (P) mechanosensory neuron', 'Neocortex spiking regular (RS) neuron', "
        f"'Neocortex spiking low threshold (LTS) neuron', 'Squid axon', 'Hodgkin-Huxley neuron', 'Teleost thalamic neuron', "
        f"'Leech heart interneuron', 'Abstract Wang-Buzsaki neuron', 'Aplysia sensory neuron', 'Hermissenda photoreceptor Type B', "
        f"'Aplysia motor neuron', 'Aplysia cultured neuron', 'Honeybee kenyon cell', 'Aplysia interneuron', 'Auditory nerve', "
        f"'CN stellate cell', 'Abstract Izhikevich neuron', 'Leech T segmental sensory neuron', 'Depressor scutorum rostralis muscle cell', "
        f"'Abstract Morris-Lecar neuron', 'Aplysia R15 bursting neuron', 'Neocortex fast spiking (FS) interneuron', 'ELL pyramidal cell', "
        f"'Dorsal Root Ganglion (DRG) cell', 'Dentate gyrus mossy cell', 'Dentate gyrus hilar cell', 'Leech S cell', "
        f"'Spinal cord lamina I neuron', 'Medial Superior Olive (MSO) cell', 'Vestibular neuron', 'Cochlear ganglion cell Type II', "
        f"'Cardiac ventricular cell', 'Neuroblastoma', 'Pituitary cell', 'Aplysia feeding CPG neurons', 'Subthalamus nucleus projection neuron', "
        f"'Hermissenda photoreceptor Type A', 'Abstract integrate-and-fire leaky neuron', 'Electric fish P- and T-type primary afferent fibers', "
        f"'Electric fish midbrain torus semicircularis neuron', 'Neocortex bitufted interneuron', 'Globus pallidus neuron', "
        f"'Crayfish identified nonspiking interneuron', 'Ventral cochlear nucleus T stellate (chopper) neuron', 'Myenteric interstitial cell of Cajal (ICCMY)', "
        f"'Intramuscular interstitial cell of Cajal (ICCIM)', 'Tritonia swim interneuron dorsal', 'Tritonia cerebral cell', "
        f"'Tritonia swim interneuron ventral', 'Turtle dorsal cortex lateral pyramidal cell', 'Turtle dorsal cortex medial pyramidal cell', "
        f"'Turtle dorsal cortex subpial cell', 'Turtle dorsal cortex stellate cell', 'Turtle dorsal cortex horizontal cell', "
        f"'Microglia', 'Macrophage', 'B lymphocyte', 'Hippocampus dissociated neuron', 'Astrocyte', 'Cerebellum golgi cell', "
        f"'Nucleus accumbens spiny projection neuron', 'GnRH neuron', 'Hippocampus CA1 basket cell', 'NG108-15 neuronal cell', "
        f"'Abstract integrate-and-fire adaptive exponential (AdEx) neuron', 'Spinal lamprey neuron', 'Leech C interneuron', "
        f"'Aplysia B31/B32 neuron', 'Locust Lobula Giant Movement Detector (LGMD) neuron', 'Fly lobular plate vertical system cell', "
        f"'Stomatogastric Ganglion (STG) Lateral Pyloric (LP) cell', 'Spinal cord motor neuron slow twitch', 'Spinal cord motor neuron fatigue resistant', "
        f"'Spinal cord motor neuron fast fatiguing', 'Spinal cord Ib interneuron', 'Spinal cord renshaw cell', 'Stick insect nonspiking interneuron', "
        f"'Neostriatum fast spiking interneuron', 'Drosophila antennal lobe DM1 projection neuron', 'Leech Retzius neuron', "
        f"'Dentate gyrus MOPP cell', 'Respiratory column neuron', 'PreBotzinger complex neuron', 'Helix pacemaker bursting neuron (RPa1)', "
        f"'Vibrissa motoneuron', 'C elegans Hermaphrodite-Specific neuron (HSN)', 'C elegans VC motor neuron', 'C elegans uterine-vulval cell (uv1)', "
        f"'Vibrissa motor plant', 'Neocortex dissociated cultured nerve cell', 'Wide dynamic range neuron', 'Entorhinal cortex stellate cell', "
        f"'Cerebellum deep nucleus neuron', 'Hippocampus CA1 stratum radiatum interneuron', 'Hippocampus CA3 stratum oriens lacunosum-moleculare interneuron', "
        f"'Superior paraolivary nucleus neuron', 'Thalamus lateral geniculate nucleus interneuron', 'Olfactory bulb main juxtaglomerular cell', "
        f"'Hippocampus CA3 stratum radiatum lacunosum-moleculare interneuron', 'Hippocampus septum medial GABAergic neuron', 'Lateral Superior Olive (LSO) cell', "
        f"'Stomatogastric ganglion (STG) pyloric dilator (PD) neuron', 'Stomatogastric ganglion (STG) pyloric neuron', 'Inferior olive neuron', "
        f"'Thalamus DLM projection neuron', 'Locus Coeruleus neuron', 'Suprachiasmatic nucleus (SCN) neuron', 'Abstract theta neuron', "
        f"'Neostriatum spiny neuron', 'Crayfish motor neuron', 'Neocortex deep neurogliaform interneuron', 'Neocortex superficial neurogliaform interneuron', "
        f"'Spinal cord sympathetic preganglionic neuron', 'Grueneberg ganglion neuron', 'Leech heart motor neuron (HE)', 'Fly vertical system tangential cell', "
        f"'Gastrointestinal tract intrinsic sensory neuron', 'Abstract integrate-and-fire fractional leaky neuron', "
        f"'Abstract single compartment conductance based cell', 'Hippocampus CA1 bistratified cell', 'Hippocampus CA1 axo-axonic cell', "
        f"'Neocortex spiking irregular interneuron', 'Olfactory bulb short axon cell', 'Fly lamina neuron', 'Fly medulla neuron', "
        f"'Hippocampus CA3 axo-axonic cells', 'Hippocampus CA1 stratum oriens lacunosum-moleculare interneuron ', 'Hippocampus CA1 PV+ fast-firing interneuron', "
        f"'Dorsal Root Ganglion cell: cold sensing', 'Olfactory bulb main tufted cell external', 'Neocortex layer 4 pyramidal cell', "
        f"'Neocortex layer 6a interneuron', 'Neocortex layer 5 interneuron', 'Neocortex layer 2-3 interneuron', 'Neocortex layer 4 interneuron', "
        f"'Brainstem neuron', 'Neocortex layer 4 neuron', 'Ventral tegmental area dopamine neuron', 'Olfactory bulb (accessory) mitral cell', "
        f"'Abstract Hindmarsh-Rose neuron', 'Pinsky-Rinzel CA1/3 pyramidal cell ', 'Mauthner cell', 'Abstract rate-based neuron', "
        f"'Neocortex primary motor area pyramidal layer 5 corticospinal cell', 'Abstract integrate-and-fire leaky neuron with dendritic subunits', "
        f"'Dentate gyrus HIPP cell', 'Ventral tegmental area GABA neuron ', 'Earthworm medial giant fiber', 'Entorhinal cortex pyramidal cell', "
        f"'Entorhinal cortex fast-spiking interneuron', 'Retina amacrine cell', 'Stomatogastric Ganglion (STG) Gastric Mill (GM) cell', 'Retina horizontal cell', "
        f"'Dopamine neuron of vlPAG/DRN', 'Multi-timescale adaptive threshold non-resetting leaky integrate and fire', "
        f"'Dorsal Root Ganglion cell: Spinal cord muscle spindle type Ia sensory fiber', 'Dorsal Root Ganglion cell: Spinal cord muscle spindle type II sensory fiber', "
        f"'Abstract integrate-and-fire neuron', 'Drosophila dendritic arborization neurons', 'Fly lobula plate T4 neuron', 'Turtle vestibular neuron', "
        f"'Urinary Bladder small-diameter DRG neuron', 'Abstract quadratic integrate-and-fire', 'Hippocampus CA1 basket cell - CCK/VIP', "
        f"'Hippocampal CA1 CR/VIP cell', 'Hypoglossal motor neuron', 'Abstract Rulkov-Bazhenov map neurons', "
        f"'Abstract integrate-and-fire leaky neuron with exponential post-synaptic current', 'ELL Medium Ganglion cell', 'Locust Giant GABAergic Neuron (GGN)', "
        f"'Drosophila ventral lateral neuron (LNV)', 'Striatal projection neuron', 'Neocortex layer 5 pyramidal cell', 'Insect photoreceptor', "
        f"'Spinal cord lamina I-III interneuron', 'Zebra Finch RA projection neuron', 'C elegans AWCon', 'C elegans motor neuron RMD', "
        f"'Spinal cord Ia interneuron', 'Dopaminergic substantia nigra neuron', 'Vestibular nucleus neuron', 'Barrel cortex L2/3 pyramidal cell', 'Pancreatic Beta Cell'].\n\n"
        f"Based on this content, please provide the most relevant cell types, just list them separated by commas, DO NOT analyze, "
        f"This is an example: type 1, type 2,..."
        )
    else:
        prompt = (
        f"You are a neuroscience expert specializing in model concepts analysis. "
        f"Given the following content:\n\n{file_content}\n\n"
        f"Please identify the most relevant model concepts from the following list. "
        f"The list includes: ['Action Potential Initiation', 'Pattern Recognition', 'Activity Patterns', 'Dendritic Action Potentials', "
        f"'Bursting', 'Ion Channel Kinetics', 'Coincidence Detection', 'Temporal Pattern Generation', 'Oscillations', "
        f"'Synchronization', 'Spatio-temporal Activity Patterns', 'Parameter Fitting', 'Simplified Models', 'Active Dendrites', "
        f"'Influence of Dendritic Geometry', 'Detailed Neuronal Models', 'Tutorial/Teaching', 'Synaptic Plasticity', "
        f"'Short-term Synaptic Plasticity', 'Axonal Action Potentials', 'Long-term Synaptic Plasticity', 'Action Potentials', "
        f"'Therapeutics', 'Facilitation', 'Post-Tetanic Potentiation', 'Depression', 'Intrinsic plasticity', 'Invertebrate', "
        f"'Methods', 'Pathophysiology', 'Epilepsy', 'Multiple sclerosis', 'Heart disease', 'Signaling pathways', "
        f"'Rate-coding model neurons', 'Synaptic Integration', 'Electrotonus', \"Parkinson's\", 'Working memory', 'Learning', "
        f"'Reinforcement Learning', 'Unsupervised Learning', 'Attractor Neural Network', 'Winner-take-all', "
        f"'Action Selection/Decision Making', 'Extracellular Fields', 'STDP', 'Brugada', 'Long-QT', 'Sleep', 'Nociception', "
        f"'Stuttering', 'Delay', 'Place cell/field', 'Calcium dynamics', 'Timothy Syndrome', 'Aging/Alzheimer`s', 'Schizophrenia', "
        f"'Addiction', 'Complementary and alternative medicine', 'Perceptual Categories', 'Magnetoencephalography', 'Conduction failure', "
        f"'Connectivity matrix', 'Biofeedback', 'Reward-modulated STDP', 'Direction Selectivity', 'Deep brain stimulation', "
        f"'Spike Frequency Adaptation', 'Parameter sensitivity', 'Maintenance', 'Sodium pump', 'Depolarization block', 'Noise Sensitivity', "
        f"'Maximum entropy models', 'Locking, mixed mode', 'Laminar Connectivity', 'Development', 'Envelope synthesis', "
        f"'Information transfer', 'G-protein coupled', 'Rebound firing', 'Intermittent block', 'Phase Response Curves', 'Erythromelalgia', "
        f"'Magnetic stimulation', 'Brain Rhythms', 'Anoxic depolarization', 'Evoked LFP', 'Sensory processing', 'Phase interference', "
        f"'Cardiac pacemaking', 'Chloride regulation', 'Synaptic-input statistic', 'Conductance distributions', 'Bifurcation', "
        f"'Cellular volume dynamics', 'Homeostasis', 'Duration Selectivity', 'Boolean network', 'Apoptosis', 'Circadian Rhythms', "
        f"'unscented Kalman filter', 'Intracortical Microstimulation', 'Orientation selectivity', 'Drug binding', 'Reliability', "
        f"'Calcium waves', 'Posture and locomotion', 'Storage/recall', 'CREB', 'Recurrent Discharge', 'Potassium buffering', "
        f"'Contrast-gain control', 'Temperature', 'Color selectivity', 'Triggered activity', 'Neurogenesis', 'Gamma oscillations', "
        f"'Spreading depression', 'Motion Detection', 'Dendritic Bistability', 'Hebbian plasticity', 'Sensory coding', 'Spatial Navigation', "
        f"'Reaction-diffusion', 'Volume transmission', 'Synaptic noise', 'Ephaptic coupling', 'Beta oscillations', 'Reservoir Computing', "
        f"'Cytokine Signaling', 'Persistent activity', 'Pattern Separation', 'Motor control', 'Memory', 'Grid cell', "
        f"'Borderline Personality Disorder (BPD)', 'Membrane Properties', 'Neuromodulation', 'Feature selectivity', 'Multiscale', "
        f"'Electrical-chemical', 'Bipolar Disorder (BP)', 'Spindles', 'Pacemaking mechanism', 'Current Dipole', 'Stimulus selectivity', "
        f"'Hallucinations', 'Respiratory control', 'Early evolution', 'Spreading depolarization', 'Markov-type model', 'Stochastic simulation', "
        f"'Autism spectrum disorder', 'Temporal Coding', 'Major Depression Disease (MDD)', 'Synaptic Amplification', 'Synaptic Convergence', "
        f"'Alcohol Use Disorder', 'Brain Tumor', 'Conductances estimation', 'Neurotransmitter dynamics', 'Olfaction', 'Vision', 'Audition', "
        f"'Vestibular', 'Touch', 'Whisking', 'Disparity estimation', 'Top-down input', 'Theta oscillations', 'Double cable', \"Huntington's\", "
        f"'Kesten Process', 'Langevin process', 'Amblyopia', 'Spatial connectivity', 'Cardiac-related electrode motion', 'Sleep-Wake transition', "
        f"'Acute hepatic encephalopathy (AHE)', 'Binocular energy model/Stereopsis', 'Soma-dendrite cross-talk', 'Receptive field', "
        f"'Paranoia', 'COVID-19', 'Eligibility traces', 'Behavioral switching', 'Impedance', 'Gain-bandwidth product (GBWP)', "
        f"'Phenomenological inductance', 'Sequence learning', 'Two-port analysis of electrotonus', 'Voltage transfer ratio', 'Equivalent PI circuit', "
        f"'Excitability', 'Subthreshold signaling', 'Analog coding', 'Energy consumption', 'Negative feedback', 'Neurite growth', 'Neurite loss', "
        f"'Structural plasticity', 'Homeostatic plasticity', 'Balanced networks', 'Pain processing', 'Evolution', 'Electrodiffusion', "
        f"'Context integration', 'Dynamic extracellular concentrations', 'Ramping', 'Effective Optokinetic Response (OKR)', 'Eyeblink Conditioning (EBC)', "
        f"'Synaptic Tagging and Capture'].\n\n"
        f"Based on this content, please provide the most relevant model concepts, just list them separated by commas, DO NOT analyze, "
        f"This is an example: concept1, concept2,..."
        )

    chat_completion = CLIENT.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )

    response_dict = chat_completion.to_dict()
    metadata = response_dict["choices"][0]["message"]["content"].strip()
    return metadata


def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_folder_dir> <output_folder_dir> <metadata_type>")
        sys.exit(1)
    
    filter_file_folder = sys.argv[1]
    metadata_type = sys.argv[3]
    if metadata_type not in ('celltype', 'modelconcept'):
        print("Currently <metadata_type> only includes the following: 'celltype', 'modelconcept'")
        sys.exit(1)

    # let the user to input current test type
    test_type = input("Enter the test type (or type 'quit' to exit): ").strip()
    if test_type.lower() == 'quit':
        print("Exiting the test.")
        sys.exit(0)
    
    # call GPT API here
    filter_files = {entry: entry.split('_')[0] for entry in os.listdir(filter_file_folder) if entry.endswith('.txt')}
    results = {}
    for filter_file, code in tqdm(filter_files.items(), desc="Processing Files", unit="file"):
        results[code] = {test_type: process_file(filter_file_folder, filter_file, metadata_type)} 
    
    output_json_folder = sys.argv[2]
    os.makedirs(output_json_folder, exist_ok=True)
    base_path = os.path.join(output_json_folder, f'{metadata_type}_{test_type}.json')
    output_json_path = base_path
    # prevent override
    counter = 1
    while os.path.exists(output_json_path):
        output_json_path = os.path.join(output_json_folder, f'{metadata_type}_{counter}.json')
        counter += 1

    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
    # example command
    # python test_filter.py ../data/concat_header ../evaluation/results celltype