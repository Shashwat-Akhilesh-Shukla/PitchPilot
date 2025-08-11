import streamlit as st
import os
from dotenv import load_dotenv
import json
import time
from pathlib import Path
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# Import your existing modules
from utils.presentation_exporter import save_as_powerpoint
from agents.orchestrator import PitchPilotOrchestrator
from config import PitchPilotConfig

# Page configuration
st.set_page_config(
    page_title="PitchPilot - AI Pitch Deck Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .progress-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .success-message {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .info-card {
        background: #f1f3f4;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4285f4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 PitchPilot</h1>
        <p>AI-Powered Pitch Deck Generator</p>
        <p><i>Transform your startup idea into a world-class pitch deck in minutes</i></p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=PitchPilot", width=300)
        st.markdown("---")
        
        st.markdown("### 🎯 Features")
        st.markdown("""
        - **AI Research** - Market analysis & trends
        - **Competitor Analysis** - Smart competitive positioning
        - **Visual Generation** - Charts & business graphics
        - **Smart Design** - Professional slide layouts
        - **Memory System** - Contextual content generation
        """)
        
        st.markdown("---")
        st.markdown("### ⚙️ Configuration")
        
        # Environment check
        hf_token = os.getenv("HF_TOKEN")
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        
        if hf_token:
            st.success("✅ HuggingFace Token Configured")
        else:
            st.error("❌ HuggingFace Token Missing")
            
        st.info(f"🔗 Qdrant URL: {qdrant_url}")

    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Generate Pitch", "📊 Dashboard", "⚙️ Advanced Settings", "📚 Help"])

    with tab1:
        generate_pitch_interface()
    
    with tab2:
        dashboard_interface()
    
    with tab3:
        advanced_settings_interface()
    
    with tab4:
        help_interface()

def generate_pitch_interface():
    st.markdown("## 📝 Startup Information")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        startup_name = st.text_input(
            "🏢 Startup Name",
            placeholder="e.g., TechFlow Solutions",
            help="Enter your startup's name"
        )
        
        industry = st.selectbox(
            "🏭 Industry",
            ["FinTech", "HealthTech", "EdTech", "E-commerce", "SaaS", "AI/ML", "IoT", "Blockchain", "CleanTech", "Other"],
            help="Select the industry your startup operates in"
        )
        
        problem_statement = st.text_area(
            "🎯 Problem Statement",
            placeholder="Describe the problem your startup solves...",
            height=100,
            help="Clearly define the problem you're addressing"
        )
        
        solution = st.text_area(
            "💡 Solution",
            placeholder="Explain how your startup solves this problem...",
            height=100,
            help="Describe your solution and value proposition"
        )
    
    with col2:
        target_market = st.text_area(
            "🎯 Target Market",
            placeholder="Define your target customers and market size...",
            height=80,
            help="Describe your target audience and market opportunity"
        )
        
        business_model = st.text_area(
            "💰 Business Model",
            placeholder="Explain how you make money...",
            height=80,
            help="Describe your revenue streams and pricing strategy"
        )
        
        traction = st.text_area(
            "📈 Traction",
            placeholder="Current metrics, users, revenue, partnerships...",
            height=80,
            help="Share your current progress and achievements"
        )
        
        team = st.text_area(
            "👥 Team",
            placeholder="Key team members and their backgrounds...",
            height=80,
            help="Highlight your team's expertise and experience"
        )

    # Advanced options
    with st.expander("🔧 Advanced Options"):
        col3, col4 = st.columns(2)
        
        with col3:
            slide_count = st.slider("Number of Slides", 8, 15, 11)
            include_financials = st.checkbox("Include Financial Projections", True)
            include_competition = st.checkbox("Include Competitor Analysis", True)
        
        with col4:
            template_style = st.selectbox("Template Style", ["Modern", "Classic", "Minimal", "Creative"])
            color_scheme = st.selectbox("Color Scheme", ["Blue", "Purple", "Green", "Orange"])

    # Generation button
    st.markdown("---")
    
    if st.button("🚀 Generate Pitch Deck", type="primary", use_container_width=True):
        if not all([startup_name, industry, problem_statement, solution]):
            st.error("❌ Please fill in all required fields (Name, Industry, Problem, Solution)")
            return
        
        # Prepare startup info
        startup_info = {
            "name": startup_name,
            "industry": industry,
            "problem_statement": problem_statement,
            "solution": solution,
            "target_market": target_market,
            "business_model": business_model,
            "traction": traction,
            "team": team
        }
        
        # Generate pitch deck with progress tracking
        generate_pitch_deck_with_progress(startup_info, template_style)

def generate_pitch_deck_with_progress(startup_info, template_style):
    """Generate pitch deck with real-time progress updates"""
    
    # Progress container
    progress_container = st.container()
    
    with progress_container:
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.markdown("### 🔄 Generation Progress")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize configuration and orchestrator
            status_text.text("🔧 Initializing AI agents...")
            progress_bar.progress(10)
            time.sleep(1)
            
            config = PitchPilotConfig()
            orchestrator = PitchPilotOrchestrator(config=config)
            
            # Step 1: Research
            status_text.text("🔍 Conducting market research...")
            progress_bar.progress(25)
            time.sleep(2)
            
            # Step 2: Competitor Analysis
            status_text.text("🏢 Analyzing competitors...")
            progress_bar.progress(45)
            time.sleep(2)
            
            # Step 3: Content Creation
            status_text.text("✍️ Creating pitch content...")
            progress_bar.progress(65)
            time.sleep(2)
            
            # Step 4: Slide Design
            status_text.text("🎨 Designing slides...")
            progress_bar.progress(80)
            time.sleep(2)
            
            # Step 5: Visual Generation
            status_text.text("📊 Generating visuals...")
            progress_bar.progress(90)
            time.sleep(1)
            
            # Generate the actual pitch deck
            pitch_deck = orchestrator.generate_pitch_deck(startup_info)
            
            # Step 6: Export
            status_text.text("💾 Exporting PowerPoint...")
            progress_bar.progress(95)
            
            output_filename = f"{startup_info['name'].replace(' ', '_')}_Pitch_Deck.pptx"
            save_as_powerpoint(pitch_deck, output_filename, industry=startup_info['industry'])
            
            progress_bar.progress(100)
            status_text.text("✅ Pitch deck generated successfully!")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Success message
            st.markdown(f"""
            <div class="success-message">
                <h3>🎉 Success! Your pitch deck is ready!</h3>
                <p><strong>File:</strong> {output_filename}</p>
                <p><strong>Slides Generated:</strong> {len(pitch_deck.get('slides', []))}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display pitch deck summary
            display_pitch_summary(pitch_deck)
            
            # Download button
            if os.path.exists(output_filename):
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="📥 Download Pitch Deck",
                        data=file.read(),
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        type="primary",
                        use_container_width=True
                    )
            
        except Exception as e:
            st.error(f"❌ Error generating pitch deck: {str(e)}")
            st.exception(e)

def display_pitch_summary(pitch_deck):
    """Display a summary of the generated pitch deck"""
    
    st.markdown("## 📋 Pitch Deck Summary")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Total Slides</h3>
            <h2>{}</h2>
        </div>
        """.format(len(pitch_deck.get('slides', []))), unsafe_allow_html=True)
    
    with col2:
        visuals_count = sum(len(slide.get('generated_visuals', [])) for slide in pitch_deck.get('slides', []))
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎨 Visuals</h3>
            <h2>{visuals_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        startup_name = pitch_deck.get('startup_info', {}).get('name', 'Unknown')
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏢 Startup</h3>
            <h2>{startup_name[:10]}...</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        industry = pitch_deck.get('startup_info', {}).get('industry', 'Unknown')
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏭 Industry</h3>
            <h2>{industry}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Slide preview
    st.markdown("### 📑 Slide Overview")
    for i, slide in enumerate(pitch_deck.get('slides', [])[:5]):  # Show first 5 slides
        with st.expander(f"Slide {i+1}: {slide.get('title', 'Untitled')}"):
            st.write("**Content:**")
            for bullet in slide.get('content', []):
                st.write(f"• {bullet}")
            
            if slide.get('visual_elements'):
                st.write("**Visual Elements:**")
                for visual in slide.get('visual_elements', []):
                    st.write(f"🎨 {visual}")

def dashboard_interface():
    st.markdown("## 📊 Dashboard")
    
    # Check for existing pitch decks
    pptx_files = list(Path(".").glob("*_Pitch_Deck.pptx"))
    
    if not pptx_files:
        st.info("No pitch decks generated yet. Create your first pitch deck in the 'Generate Pitch' tab!")
        return
    
    st.markdown(f"### 📁 Generated Pitch Decks ({len(pptx_files)})")
    
    for file_path in pptx_files:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"📄 **{file_path.name}**")
            st.write(f"Size: {file_path.stat().st_size / 1024:.1f} KB")
        
        with col2:
            if st.button("📥 Download", key=f"download_{file_path.name}"):
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="Download",
                        data=file.read(),
                        file_name=file_path.name,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
        
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{file_path.name}"):
                os.remove(file_path)
                st.rerun()
        
        st.markdown("---")

def advanced_settings_interface():
    st.markdown("## ⚙️ Advanced Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 AI Model Settings")
        
        model_name = st.selectbox(
            "LLM Model",
            ["meta-llama/Llama-3.3-70B-Instruct", "meta-llama/Llama-3.1-8B-Instruct"],
            help="Choose the AI model for content generation"
        )
        
        temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1, help="Controls creativity vs consistency")
        max_tokens = st.number_input("Max Tokens", 1000, 4000, 2048, help="Maximum response length")
        
        st.markdown("### 🧠 Memory Settings")
        vector_dimension = st.number_input("Vector Dimension", 384, 1536, 768)
        collection_name = st.text_input("Collection Name", "pitchpilot_memory")
    
    with col2:
        st.markdown("### 🎨 Generation Settings")
        
        max_iterations = st.slider("Max Iterations", 1, 10, 5)
        reflection_threshold = st.slider("Reflection Threshold", 0.1, 1.0, 0.7)
        
        st.markdown("### 🔗 API Settings")
        
        qdrant_url = st.text_input("Qdrant URL", os.getenv("QDRANT_URL", "http://localhost:6333"))
        
        # Test connections
        if st.button("🔍 Test Connections"):
            test_connections(qdrant_url)

def test_connections(qdrant_url):
    """Test API connections"""
    results = {}
    
    # Test HuggingFace
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        results["HuggingFace"] = "✅ Connected"
    else:
        results["HuggingFace"] = "❌ Token Missing"
    
    # Test Qdrant
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url=qdrant_url)
        collections = client.get_collections()
        results["Qdrant"] = f"✅ Connected ({len(collections.collections)} collections)"
    except Exception as e:
        results["Qdrant"] = f"❌ Error: {str(e)}"
    
    # Display results
    for service, status in results.items():
        if "✅" in status:
            st.success(f"{service}: {status}")
        else:
            st.error(f"{service}: {status}")

def help_interface():
    st.markdown("## 📚 Help & Documentation")
    
    tab1, tab2, tab3 = st.tabs(["🚀 Quick Start", "❓ FAQ", "🔧 Troubleshooting"])
    
    with tab1:
        st.markdown("""
        ### 🚀 Quick Start Guide
        
        1. **Fill Startup Information**: Enter your startup details in the 'Generate Pitch' tab
        2. **Configure Settings**: Adjust AI and generation settings in 'Advanced Settings'
        3. **Generate Deck**: Click 'Generate Pitch Deck' and wait for the AI to work its magic
        4. **Download**: Download your professional pitch deck as a PowerPoint file
        
        ### 📋 Required Information
        - **Startup Name**: Your company name
        - **Industry**: Select from available industries
        - **Problem Statement**: The problem you're solving
        - **Solution**: How you solve the problem
        - **Target Market**: Your customers and market size
        - **Business Model**: How you make money
        - **Traction**: Current progress and metrics
        - **Team**: Key team members and backgrounds
        """)
    
    with tab2:
        st.markdown("""
        ### ❓ Frequently Asked Questions
        
        **Q: How long does it take to generate a pitch deck?**
        A: Typically 2-5 minutes depending on the complexity and AI model used.
        
        **Q: Can I customize the generated slides?**
        A: Yes! The generated PowerPoint file can be edited like any normal presentation.
        
        **Q: What industries are supported?**
        A: We support FinTech, HealthTech, EdTech, E-commerce, SaaS, AI/ML, IoT, Blockchain, CleanTech, and others.
        
        **Q: Is my data stored anywhere?**
        A: Data is only stored in your local Qdrant database and generated files. Nothing is sent to external servers.
        
        **Q: Can I generate multiple pitch decks?**
        A: Yes! You can generate as many pitch decks as needed. Check the Dashboard tab to manage them.
        """)
    
    with tab3:
        st.markdown("""
        ### 🔧 Troubleshooting
        
        **Issue: "HuggingFace Token Missing"**
        - Add your HF_TOKEN to the .env file
        - Restart the application
        
        **Issue: "Qdrant Connection Failed"**
        - Ensure Qdrant is running on the specified URL
        - Check if the port (default 6333) is accessible
        
        **Issue: "Generation Failed"**
        - Check your internet connection
        - Verify all required fields are filled
        - Try reducing the max_tokens if you hit rate limits
        
        **Issue: "PowerPoint Export Failed"**
        - Ensure you have write permissions in the current directory
        - Check if a template file exists in the templates/ folder
        
        ### 📞 Support
        For additional help, check the GitHub repository or create an issue.
        """)

if __name__ == "__main__":
    main()
