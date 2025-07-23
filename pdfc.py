import streamlit as st
from fpdf import FPDF
from PIL import Image
import base64
import io
import datetime
import os
import tempfile
import uuid

# Configure page
st.set_page_config(
    page_title="VASTAS Professional CFD Report Generator", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        color: #1B4F72;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #EBF5FB, #D6EAF8);
        border-radius: 10px;
        border-left: 5px solid #2874A6;
    }
    .section-header {
        color: #2E86C1;
        border-bottom: 2px solid #3498DB;
        padding-bottom: 10px;
        margin-top: 2rem;
        font-weight: bold;
    }
    .info-box {
        background-color: #EBF5FB;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid #3498DB;
    }
    .warning-box {
        background-color: #FDF2E9;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid #F39C12;
    }
    .stButton>button {
        background-color: #2874A6 !important;
        color: white !important;
        font-weight: bold !important;
        padding: 10px 24px !important;
        border-radius: 5px !important;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1B4F72 !important;
        transform: scale(1.02);
    }
    .formula-display {
        background-color: #F7F9F9;
        padding: 15px;
        border-radius: 5px;
        font-family: "Courier New", monospace;
        border: 1px solid #D6DBDF;
        margin: 10px 0;
    }
    .image-preview {
        border: 2px solid #D6DBDF;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
        background-color: #FAFAFA;
    }
    .metrics-container {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    .metric-box {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #E9ECEF;
    }
</style>
""", unsafe_allow_html=True)

class ProfessionalPDFGenerator(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.WIDTH = 210
        self.HEIGHT = 297
        self.company_logo = None
        
    def header(self):
        # Company logo and header
        if self.company_logo:
            try:
                self.image(self.company_logo, x=15, y=8, w=25)
            except:
                pass
        
        self.set_font('Arial', 'B', 20)
        self.set_text_color(27, 79, 114)  # Professional blue
        self.cell(0, 15, 'COMPUTATIONAL FLUID DYNAMICS', 0, 1, 'C')
        self.cell(0, 10, 'ANALYSIS REPORT', 0, 1, 'C')
        
        # Add line
        self.set_draw_color(52, 152, 219)
        self.set_line_width(1)
        self.line(20, 35, 190, 35)
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | CFD Analysis Report | Generated on {datetime.datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'C')
    
    def add_title_page(self, report_data):
        self.add_page()
        self.ln(30)
        
        # Main title
        self.set_font('Arial', 'B', 24)
        self.set_text_color(27, 79, 114)
        self.cell(0, 15, report_data['title'], 0, 1, 'C')
        self.ln(20)
        
        # Report details box
        self.set_fill_color(235, 245, 251)
        self.rect(30, self.get_y(), 150, 80, 'F')
        
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.ln(10)
        self.cell(0, 10, 'REPORT DETAILS', 0, 1, 'C')
        self.ln(5)
        
        self.set_font('Arial', '', 12)
        details = [
            f"Project: {report_data['project_name']}",
            f"Analyst: {report_data['analyst']}",
            f"Company: {report_data['company']}",
            f"Date: {report_data['date']}",
            f"Version: {report_data['version']}",
            f"Software: {report_data['cfd_software']}"
        ]
        
        for detail in details:
            self.cell(0, 8, detail, 0, 1, 'C')
        
        self.ln(30)
        
        # Add confidentiality notice
        self.set_font('Arial', 'I', 10)
        self.set_text_color(128, 128, 128)
        self.multi_cell(0, 5, 
            "CONFIDENTIAL: This document contains proprietary information and is intended solely for the use of the intended recipient(s). "
            "Any reproduction or distribution of this document, in whole or in part, without written consent is strictly prohibited.",
            0, 'C')
    
    def add_section_header(self, title, level=1):
        self.ln(10)
        if level == 1:
            self.set_font('Arial', 'B', 16)
            self.set_text_color(46, 134, 193)
        else:
            self.set_font('Arial', 'B', 14)
            self.set_text_color(84, 153, 199)
        
        self.cell(0, 10, title, 0, 1)
        
        # Add underline for main sections
        if level == 1:
            self.set_draw_color(52, 152, 219)
            self.line(10, self.get_y()-2, 200, self.get_y()-2)
        
        self.ln(5)
        self.set_text_color(0, 0, 0)
    
    def add_section_content(self, content):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, content)
        self.ln(5)
    
    def add_table(self, headers, data):
        self.set_font('Arial', 'B', 10)
        
        # Table headers
        col_width = (self.WIDTH - 20) / len(headers)
        for header in headers:
            self.cell(col_width, 8, header, 1, 0, 'C')
        self.ln()
        
        # Table data
        self.set_font('Arial', '', 9)
        for row in data:
            for item in row:
                self.cell(col_width, 6, str(item), 1, 0, 'C')
            self.ln()
        self.ln(5)
    
    def add_image_with_caption(self, image_path, caption, width=None):
        if not os.path.exists(image_path):
            return
            
        try:
            if width is None:
                width = self.WIDTH - 40
            
            # Add image
            x_pos = (self.WIDTH - width) / 2
            self.image(image_path, x=x_pos, w=width)
            
            # Add caption
            self.set_font('Arial', 'I', 10)
            self.set_text_color(64, 64, 64)
            self.cell(0, 8, f"Figure: {caption}", 0, 1, 'C')
            self.ln(5)
            self.set_text_color(0, 0, 0)
        except:
            self.set_font('Arial', 'I', 10)
            self.cell(0, 8, f"[Image could not be displayed: {caption}]", 0, 1, 'C')
            self.ln(5)
    
    def add_formula_box(self, description, formula):
        self.add_section_header(description, level=2)
        
        # Formula box
        self.set_fill_color(247, 249, 249)
        formula_lines = formula.split('\n')
        box_height = len(formula_lines) * 6 + 10
        
        self.rect(20, self.get_y(), self.WIDTH-40, box_height, 'F')
        self.ln(5)
        
        self.set_font('Courier', '', 10)
        for line in formula_lines:
            self.cell(0, 6, line, 0, 1, 'C')
        
        self.ln(5)
        self.set_font('Arial', '', 11)

def save_uploaded_image(uploaded_file, temp_dir):
    """Save uploaded image to temporary directory and return path"""
    if uploaded_file is None:
        return None
    
    try:
        # Generate unique filename
        file_extension = uploaded_file.name.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        img_path = os.path.join(temp_dir, unique_filename)
        
        # Open and save image
        img = Image.open(uploaded_file)
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(img_path, 'JPEG', quality=85)
        
        return img_path
    except Exception as e:
        st.error(f"Error saving image: {str(e)}")
        return None

def create_professional_pdf(report_data, temp_dir):
    """Generate professional PDF report"""
    pdf = ProfessionalPDFGenerator()
    
    # Set company logo if available
    if report_data['company_logo']:
        pdf.company_logo = save_uploaded_image(report_data['company_logo'], temp_dir)
    
    # Title page
    pdf.add_title_page(report_data)
    
    # Table of Contents
    pdf.add_page()
    pdf.add_section_header("TABLE OF CONTENTS")
    toc_items = [
        "1. Executive Summary",
        "2. Problem Definition & Objectives",
        "3. Geometry & Domain",
        "4. Mesh Generation & Quality",
        "5. Boundary Conditions",
        "6. Methodology & Solution Setup",
        "7. Results & Discussion",
        "8. Convergence Analysis",
        "9. Validation & Verification",
        "10. Conclusions & Recommendations"
    ]
    
    pdf.set_font('Arial', '', 11)
    for item in toc_items:
        pdf.cell(0, 8, item, 0, 1)
    
    # Executive Summary
    pdf.add_page()
    pdf.add_section_header("1. EXECUTIVE SUMMARY")
    pdf.add_section_content(report_data['executive_summary'])
    
    # Problem Definition
    pdf.add_section_header("2. PROBLEM DEFINITION & OBJECTIVES")
    pdf.add_section_content(report_data['problem_definition'])
    
    # Geometry
    pdf.add_section_header("3. GEOMETRY & DOMAIN")
    pdf.add_section_content(report_data['geometry_description'])
    
    # Mesh Quality
    pdf.add_section_header("4. MESH GENERATION & QUALITY")
    pdf.add_section_content(report_data['mesh_details'])
    
    # Add mesh quality table if provided
    if report_data['mesh_quality_data']:
        pdf.add_section_header("Mesh Quality Metrics", level=2)
        headers = ["Parameter", "Value", "Acceptable Range", "Status"]
        pdf.add_table(headers, report_data['mesh_quality_data'])
    
    # Boundary Conditions
    pdf.add_section_header("5. BOUNDARY CONDITIONS")
    pdf.add_section_content(report_data['boundary_conditions'])
    
    # Add boundary conditions table
    if report_data['boundary_conditions_table']:
        headers = ["Boundary", "Type", "Value/Condition", "Description"]
        pdf.add_table(headers, report_data['boundary_conditions_table'])
    
    # Methodology
    pdf.add_section_header("6. METHODOLOGY & SOLUTION SETUP")
    pdf.add_section_content(report_data['methodology'])
    
    # Solution parameters table
    if report_data['solution_parameters']:
        pdf.add_section_header("Solution Parameters", level=2)
        headers = ["Parameter", "Value", "Description"]
        pdf.add_table(headers, report_data['solution_parameters'])
    
    # Results
    pdf.add_section_header("7. RESULTS & DISCUSSION")
    pdf.add_section_content(report_data['results'])
    
    # Add result images
    for img_data in report_data['result_images']:
        if img_data['file']:
            img_path = save_uploaded_image(img_data['file'], temp_dir)
            if img_path:
                pdf.add_image_with_caption(img_path, img_data['caption'])
    
    # Convergence Analysis
    pdf.add_section_header("8. CONVERGENCE ANALYSIS")
    pdf.add_section_content(report_data['convergence_analysis'])
    
    # Add convergence images
    for img_data in report_data['convergence_images']:
        if img_data['file']:
            img_path = save_uploaded_image(img_data['file'], temp_dir)
            if img_path:
                pdf.add_image_with_caption(img_path, img_data['caption'])
    
    # Validation
    pdf.add_section_header("9. VALIDATION & VERIFICATION")
    pdf.add_section_content(report_data['validation'])
    
    # Formulas
    if report_data['formulas']:
        pdf.add_page()
        pdf.add_section_header("GOVERNING EQUATIONS & FORMULAS")
        for i, formula in enumerate(report_data['formulas']):
            if formula['description'] and formula['formula']:
                pdf.add_formula_box(f"Equation {i+1}: {formula['description']}", formula['formula'])
    
    # Conclusions
    pdf.add_section_header("10. CONCLUSIONS & RECOMMENDATIONS")
    pdf.add_section_content(report_data['conclusions'])
    
    return pdf

def initialize_session_state():
    """Initialize all session state variables"""
    if 'report_data' not in st.session_state:
        st.session_state.report_data = {
            # Basic Info
            'title': "CFD Analysis Report",
            'project_name': "",
            'analyst': "",
            'company': "",
            'date': datetime.datetime.now().strftime("%Y-%m-%d"),
            'version': "1.0",
            'cfd_software': "ANSYS Fluent",
            'company_logo': None,
            
            # Report Sections
            'executive_summary': "",
            'problem_definition': "",
            'geometry_description': "",
            'mesh_details': "",
            'boundary_conditions': "",
            'methodology': "",
            'results': "",
            'convergence_analysis': "",
            'validation': "",
            'conclusions': "",
            
            # Tables and Data
            'boundary_conditions_table': [],
            'mesh_quality_data': [],
            'solution_parameters': [],
            
            # Images
            'result_images': [],
            'convergence_images': [],
            
            # Formulas
            'formulas': [{'description': '', 'formula': ''}]
        }

def main():
    # Initialize session state
    initialize_session_state()
    
    # Main header
    st.markdown('<div class="main-header">VASTAS Professional CFD Report Generator</div>', unsafe_allow_html=True)
    
    # Sidebar for report metadata
    with st.sidebar:
        st.markdown("### 📋 Report Information")
        
        # Company branding
        st.markdown("#### Company Branding")
        st.session_state.report_data['company_logo'] = st.file_uploader(
            "Company Logo", 
            type=["png", "jpg", "jpeg"],
            key="logo_uploader"
        )
        
        # Basic information
        st.session_state.report_data['title'] = st.text_input(
            "Report Title", 
            st.session_state.report_data['title']
        )
        
        st.session_state.report_data['project_name'] = st.text_input(
            "Project Name", 
            st.session_state.report_data['project_name']
        )
        
        st.session_state.report_data['company'] = st.text_input(
            "Company Name", 
            st.session_state.report_data['company']
        )
        
        st.session_state.report_data['analyst'] = st.text_input(
            "Lead Analyst", 
            st.session_state.report_data['analyst']
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.report_data['date'] = st.date_input(
                "Report Date", 
                datetime.datetime.strptime(st.session_state.report_data['date'], "%Y-%m-%d")
            ).strftime("%Y-%m-%d")
        
        with col2:
            st.session_state.report_data['version'] = st.text_input(
                "Version", 
                st.session_state.report_data['version']
            )
        
        st.session_state.report_data['cfd_software'] = st.selectbox(
            "CFD Software",
            ["ANSYS Fluent", "ANSYS CFX", "OpenFOAM", "COMSOL", "STAR-CCM+", "SU2", "Other"],
            index=0
        )
        
        # Progress indicator
        st.markdown("---")
        st.markdown("### 📊 Report Progress")
        
        sections_completed = sum([
            bool(st.session_state.report_data['executive_summary']),
            bool(st.session_state.report_data['problem_definition']),
            bool(st.session_state.report_data['boundary_conditions']),
            bool(st.session_state.report_data['methodology']),
            bool(st.session_state.report_data['results']),
            bool(st.session_state.report_data['conclusions'])
        ])
        
        progress = sections_completed / 6
        st.progress(progress)
        st.write(f"Completed: {sections_completed}/6 main sections")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Report Content", 
        "🔧 Technical Details", 
        "📊 Results & Analysis", 
        "📈 Validation", 
        "🔄 Generate Report"
    ])
    
    with tab1:
        st.markdown('<h2 class="section-header">Report Content</h2>', unsafe_allow_html=True)
        
        # Executive Summary
        st.markdown("#### Executive Summary")
        st.markdown('<div class="info-box">Provide a concise overview of the analysis objectives, key findings, and recommendations (2-3 paragraphs).</div>', unsafe_allow_html=True)
        st.session_state.report_data['executive_summary'] = st.text_area(
            "Executive Summary Content:",
            st.session_state.report_data['executive_summary'],
            height=150,
            key="exec_summary"
        )
        
        # Problem Definition
        st.markdown("#### Problem Definition & Objectives")
        st.session_state.report_data['problem_definition'] = st.text_area(
            "Describe the engineering problem, analysis objectives, and scope:",
            st.session_state.report_data['problem_definition'],
            height=150,
            key="problem_def"
        )
        
        # Geometry Description
        st.markdown("#### Geometry & Domain Description")
        st.session_state.report_data['geometry_description'] = st.text_area(
            "Describe the computational domain, geometry simplifications, and key dimensions:",
            st.session_state.report_data['geometry_description'],
            height=120,
            key="geometry"
        )
        
        # Conclusions
        st.markdown("#### Conclusions & Recommendations")
        st.session_state.report_data['conclusions'] = st.text_area(
            "Summarize key findings, conclusions, and engineering recommendations:",
            st.session_state.report_data['conclusions'],
            height=150,
            key="conclusions"
        )
    
    with tab2:
        st.markdown('<h2 class="section-header">Technical Details</h2>', unsafe_allow_html=True)
        
        # Mesh Details
        st.markdown("#### Mesh Generation & Quality")
        st.session_state.report_data['mesh_details'] = st.text_area(
            "Describe mesh generation strategy, element types, refinement regions, and quality metrics:",
            st.session_state.report_data['mesh_details'],
            height=120,
            key="mesh_details"
        )
        
        # Mesh Quality Table
        st.markdown("#### Mesh Quality Metrics")
        with st.expander("Add Mesh Quality Data"):
            if st.button("Add Mesh Quality Row"):
                st.session_state.report_data['mesh_quality_data'].append(["", "", "", ""])
                st.rerun()
            
            for i, row in enumerate(st.session_state.report_data['mesh_quality_data']):
                cols = st.columns([2, 2, 2, 2, 1])
                with cols[0]:
                    st.session_state.report_data['mesh_quality_data'][i][0] = st.text_input(f"Parameter {i+1}", row[0], key=f"mesh_param_{i}")
                with cols[1]:
                    st.session_state.report_data['mesh_quality_data'][i][1] = st.text_input(f"Value {i+1}", row[1], key=f"mesh_val_{i}")
                with cols[2]:
                    st.session_state.report_data['mesh_quality_data'][i][2] = st.text_input(f"Range {i+1}", row[2], key=f"mesh_range_{i}")
                with cols[3]:
                    st.session_state.report_data['mesh_quality_data'][i][3] = st.selectbox(f"Status {i+1}", ["Good", "Acceptable", "Poor"], key=f"mesh_status_{i}")
                with cols[4]:
                    if st.button("❌", key=f"del_mesh_{i}"):
                        st.session_state.report_data['mesh_quality_data'].pop(i)
                        st.rerun()
        
        # Boundary Conditions
        st.markdown("#### Boundary Conditions")
        st.session_state.report_data['boundary_conditions'] = st.text_area(
            "Describe the boundary conditions applied in the simulation:",
            st.session_state.report_data['boundary_conditions'],
            height=120,
            key="boundary_conditions"
        )
        
        # Boundary Conditions Table
        st.markdown("#### Boundary Conditions Table")
        with st.expander("Add Boundary Condition Details"):
            if st.button("Add Boundary Condition"):
                st.session_state.report_data['boundary_conditions_table'].append(["", "", "", ""])
                st.rerun()
            
            for i, row in enumerate(st.session_state.report_data['boundary_conditions_table']):
                cols = st.columns([2, 2, 2, 3, 1])
                with cols[0]:
                    st.session_state.report_data['boundary_conditions_table'][i][0] = st.text_input(f"Boundary {i+1}", row[0], key=f"bc_name_{i}")
                with cols[1]:
                    st.session_state.report_data['boundary_conditions_table'][i][1] = st.selectbox(
                        f"Type {i+1}", 
                        ["Inlet", "Outlet", "Wall", "Symmetry", "Pressure Outlet", "Mass Flow Inlet"],
                        key=f"bc_type_{i}"
                    )
                with cols[2]:
                    st.session_state.report_data['boundary_conditions_table'][i][2] = st.text_input(f"Value {i+1}", row[2], key=f"bc_val_{i}")
                with cols[3]:
                    st.session_state.report_data['boundary_conditions_table'][i][3] = st.text_input(f"Description {i+1}", row[3], key=f"bc_desc_{i}")
                with cols[4]:
                    if st.button("❌", key=f"del_bc_{i}"):
                        st.session_state.report_data['boundary_conditions_table'].pop(i)
                        st.rerun()
        
        # Methodology
        st.markdown("#### Methodology & Solution Setup")
        st.session_state.report_data['methodology'] = st.text_area(
            "Describe solver settings, turbulence models, discretization schemes, and solution methods:",
            st.session_state.report_data['methodology'],
            height=150,
            key="methodology"
        )
        
        # Solution Parameters
        st.markdown("#### Solution Parameters")
        with st.expander("Add Solution Parameters"):
            if st.button("Add Parameter"):
                st.session_state.report_data['solution_parameters'].append(["", "", ""])
                st.rerun()
            
            for i, row in enumerate(st.session_state.report_data['solution_parameters']):
                cols = st.columns([2, 2, 3, 1])
                with cols[0]:
                    st.session_state.report_data['solution_parameters'][i][0] = st.text_input(f"Parameter {i+1}", row[0], key=f"sol_param_{i}")
                with cols[1]:
                    st.session_state.report_data['solution_parameters'][i][1] = st.text_input(f"Value {i+1}", row[1], key=f"sol_val_{i}")
                with cols[2]:
                    st.session_state.report_data['solution_parameters'][i][2] = st.text_input(f"Description {i+1}", row[2], key=f"sol_desc_{i}")
                with cols[3]:
                    if st.button("❌", key=f"del_sol_{i}"):
                        st.session_state.report_data['solution_parameters'].pop(i)
                        st.rerun()
    
    with tab3:
        st.markdown('<h2 class="section-header">Results & Analysis</h2>', unsafe_allow_html=True)
        
        # Results Section
        st.markdown("#### Results & Discussion")
        st.session_state.report_data['results'] = st.text_area(
            "Present and discuss the simulation results, including key findings and physical interpretations:",
            st.session_state.report_data['results'],
            height=200,
            key="results"
        )
        
        # Result Images
        st.markdown("#### Result Images")
        with st.expander("Upload Result Images", expanded=True):
            new_result_image = st.file_uploader(
                "Select result image", 
                type=["png", "jpg", "jpeg"],
                key="new_result_image"
            )
            
            if new_result_image:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(new_result_image, width=200)
                with col2:
                    caption = st.text_input("Image Caption", key="result_caption")
                    if st.button("Add Result Image", key="add_result_img"):
                        st.session_state.report_data['result_images'].append({
                            'file': new_result_image,
                            'caption': caption
                        })
                        st.success("Result image added!")
                        st.rerun()
        
        # Display current result images
        if st.session_state.report_data['result_images']:
            st.markdown("**Current Result Images:**")
            for i, img_data in enumerate(st.session_state.report_data['result_images']):
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        st.image(img_data['file'], width=150)
                    with col2:
                        st.markdown(f"**Caption:** {img_data['caption']}")
                    with col3:
                        if st.button(f"Remove", key=f"del_result_img_{i}"):
                            st.session_state.report_data['result_images'].pop(i)
                            st.rerun()
                    st.markdown("---")
        
        # Convergence Analysis
        st.markdown("#### Convergence Analysis")
        st.session_state.report_data['convergence_analysis'] = st.text_area(
            "Discuss convergence criteria, residuals behavior, and solution stability:",
            st.session_state.report_data['convergence_analysis'],
            height=120,
            key="convergence_analysis"
        )
        
        # Convergence Images
        st.markdown("#### Convergence Plot Images")
        with st.expander("Upload Convergence Plots"):
            new_conv_image = st.file_uploader(
                "Select convergence plot", 
                type=["png", "jpg", "jpeg"],
                key="new_conv_image"
            )
            
            if new_conv_image:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(new_conv_image, width=200)
                with col2:
                    conv_caption = st.text_input("Convergence Plot Caption", key="conv_caption")
                    if st.button("Add Convergence Plot", key="add_conv_img"):
                        st.session_state.report_data['convergence_images'].append({
                            'file': new_conv_image,
                            'caption': conv_caption
                        })
                        st.success("Convergence plot added!")
                        st.rerun()
        
        # Display current convergence images
        if st.session_state.report_data['convergence_images']:
            st.markdown("**Current Convergence Plots:**")
            for i, img_data in enumerate(st.session_state.report_data['convergence_images']):
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        st.image(img_data['file'], width=150)
                    with col2:
                        st.markdown(f"**Caption:** {img_data['caption']}")
                    with col3:
                        if st.button(f"Remove", key=f"del_conv_img_{i}"):
                            st.session_state.report_data['convergence_images'].pop(i)
                            st.rerun()
                    st.markdown("---")
        
        # Governing Equations
        st.markdown("#### Governing Equations & Formulas")
        st.markdown('<div class="info-box">Add the key mathematical formulas and governing equations used in the analysis.</div>', unsafe_allow_html=True)
        
        for i, formula in enumerate(st.session_state.report_data['formulas']):
            with st.container():
                st.markdown(f"**Equation {i+1}**")
                cols = st.columns([3, 1])
                with cols[0]:
                    st.session_state.report_data['formulas'][i]['description'] = st.text_input(
                        "Equation Description",
                        formula['description'],
                        key=f"formula_desc_{i}"
                    )
                with cols[1]:
                    if len(st.session_state.report_data['formulas']) > 1:
                        if st.button("❌ Remove", key=f"del_formula_{i}"):
                            st.session_state.report_data['formulas'].pop(i)
                            st.rerun()
                
                st.session_state.report_data['formulas'][i]['formula'] = st.text_area(
                    "Formula (LaTeX or mathematical notation)",
                    formula['formula'],
                    height=100,
                    key=f"formula_content_{i}"
                )
                
                # Preview formula
                if formula['formula']:
                    st.markdown('<div class="formula-display">', unsafe_allow_html=True)
                    st.code(formula['formula'])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("---")
        
        if st.button("➕ Add Another Formula"):
            st.session_state.report_data['formulas'].append({'description': '', 'formula': ''})
            st.rerun()
    
    with tab4:
        st.markdown('<h2 class="section-header">Validation & Verification</h2>', unsafe_allow_html=True)
        
        st.markdown("#### Validation & Verification")
        st.markdown('<div class="info-box">Describe validation against experimental data, analytical solutions, or literature comparisons. Include verification studies such as mesh independence and time step sensitivity.</div>', unsafe_allow_html=True)
        
        st.session_state.report_data['validation'] = st.text_area(
            "Validation and Verification Discussion:",
            st.session_state.report_data['validation'],
            height=200,
            key="validation"
        )
        
        # Validation metrics
        st.markdown("#### Key Validation Metrics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("Mesh Independence", "✓ Achieved", "< 2% change")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("Residuals", "Converged", "< 1e-6")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("Mass Balance", "Satisfied", "< 0.1% error")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        st.markdown('<h2 class="section-header">Generate Professional Report</h2>', unsafe_allow_html=True)
        
        # Report summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Report Summary")
            st.info(f"""
            **Title:** {st.session_state.report_data['title']}
            **Project:** {st.session_state.report_data['project_name']}
            **Analyst:** {st.session_state.report_data['analyst']}
            **Company:** {st.session_state.report_data['company']}
            **Date:** {st.session_state.report_data['date']}
            """)
        
        with col2:
            st.markdown("#### Content Statistics")
            stats = {
                "Result Images": len(st.session_state.report_data['result_images']),
                "Convergence Plots": len(st.session_state.report_data['convergence_images']),
                "Boundary Conditions": len(st.session_state.report_data['boundary_conditions_table']),
                "Solution Parameters": len(st.session_state.report_data['solution_parameters']),
                "Formulas": len([f for f in st.session_state.report_data['formulas'] if f['description']]),
                "Mesh Quality Metrics": len(st.session_state.report_data['mesh_quality_data'])
            }
            
            for key, value in stats.items():
                st.metric(key, value)
        
        # Validation checks
        st.markdown("#### Pre-Generation Checklist")
        
        required_fields = {
            "Executive Summary": bool(st.session_state.report_data['executive_summary']),
            "Problem Definition": bool(st.session_state.report_data['problem_definition']),
            "Boundary Conditions": bool(st.session_state.report_data['boundary_conditions']),
            "Methodology": bool(st.session_state.report_data['methodology']),
            "Results": bool(st.session_state.report_data['results']),
            "Conclusions": bool(st.session_state.report_data['conclusions'])
        }
        
        all_required_complete = all(required_fields.values())
        
        for field, completed in required_fields.items():
            if completed:
                st.success(f"✅ {field} - Complete")
            else:
                st.error(f"❌ {field} - Missing")
        
        if not all_required_complete:
            st.warning("⚠️ Please complete all required sections before generating the report.")
        
        # Generate button
        st.markdown("---")
        
        if st.button("🚀 Generate Professional CFD Report", disabled=not all_required_complete):
            if not all_required_complete:
                st.error("Please complete all required sections first.")
                return
            
            with st.spinner("Generating professional PDF report... This may take a few moments."):
                try:
                    # Create temporary directory
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Generate PDF
                        pdf = create_professional_pdf(st.session_state.report_data, temp_dir)
                        
                        # Save PDF to bytes
                        pdf_output = os.path.join(temp_dir, "professional_cfd_report.pdf")
                        pdf.output(pdf_output)
                        
                        # Read PDF file
                        with open(pdf_output, "rb") as f:
                            pdf_bytes = f.read()
                        
                        # Success message
                        st.success("✅ Professional CFD report generated successfully!")
                        
                        # Download button
                        filename = f"{st.session_state.report_data['project_name'].replace(' ', '_')}_CFD_Report.pdf" if st.session_state.report_data['project_name'] else "CFD_Analysis_Report.pdf"
                        
                        st.download_button(
                            label="📥 Download Professional CFD Report",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        # Additional info
                        st.info(f"""
                        📊 **Report Statistics:**
                        - Total pages: ~{10 + len(st.session_state.report_data['result_images']) + len(st.session_state.report_data['convergence_images'])}
                        - File size: {len(pdf_bytes) / 1024:.1f} KB
                        - Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        """)
                        
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
                    st.error("Please check that all images are valid and try again.")
        
        # Tips for professional reports
        st.markdown("---")
        st.markdown("#### 💡 Tips for Professional CFD Reports")
        
        tips = [
            "Include high-quality, clearly labeled figures with proper captions",
            "Provide quantitative results with appropriate units and significant figures",
            "Document all assumptions and limitations clearly",
            "Include mesh independence and convergence studies",
            "Compare results with available experimental data or analytical solutions",
            "Use consistent terminology and notation throughout the report",
            "Provide clear engineering recommendations based on the analysis"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")

if __name__ == "__main__":
    main()