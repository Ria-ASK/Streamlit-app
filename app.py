"""
SAP SoD RISK ANALYSIS - WEB APPLICATION
========================================
Streamlit-based web interface for SAP GRC compliance analysis.

Features:
- Drag & drop file upload
- Real-time analysis progress
- Interactive visualizations
- Instant report downloads
- Mobile & desktop compatible

Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from collections import defaultdict
from itertools import combinations
import io
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="SAP SoD Risk Analysis",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS STYLING
# =====================================================
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# ANALYSIS FUNCTIONS
# =====================================================
@st.cache_data
def load_rule_book(file):
    """Load and process rule book"""
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.upper()
    return df

def process_rule_book(rule_df):
    """Build conflict pairs with risk factors"""
    conflict_risk_map = {}
    
    for _, row in rule_df.iterrows():
        t1 = str(row['TCODE1']).strip().upper()
        t2 = str(row['TCODE2']).strip().upper()
        risk = str(row['ASK_RISK']).strip()
        
        if t1 and t2 and t1 != 'NAN' and t2 != 'NAN' and t1 != t2:
            pair = tuple(sorted((t1, t2)))
            if pair not in conflict_risk_map:
                conflict_risk_map[pair] = risk
    
    return conflict_risk_map

def process_user_access(user_df):
    """Build user and role mappings"""
    user_df.columns = user_df.columns.str.strip().str.upper()
    
    user_role_tcodes = defaultdict(lambda: defaultdict(set))
    role_to_tcodes = defaultdict(set)
    
    for _, row in user_df.iterrows():
        user = str(row['USER NAME']).strip()
        role = str(row['ROLE']).strip()
        tcode = str(row['AUTHORIZATION VALUE']).strip().upper()
        
        if user and role and tcode and tcode != 'NAN':
            user_role_tcodes[user][role].add(tcode)
            role_to_tcodes[role].add(tcode)
    
    return user_role_tcodes, role_to_tcodes

def analyze_violations(user_role_tcodes, role_to_tcodes, conflict_risk_map):
    """Detect user-level and role-level violations"""
    
    # User-level violations
    user_violations = []
    for user, roles_dict in user_role_tcodes.items():
        for role, tcodes in roles_dict.items():
            for t1, t2 in combinations(tcodes, 2):
                pair = tuple(sorted((t1, t2)))
                if pair in conflict_risk_map:
                    user_violations.append({
                        'USER_NAME': user,
                        'ROLE': role,
                        'TCODE_1': pair[0],
                        'TCODE_2': pair[1],
                        'RISK_FACTOR': conflict_risk_map[pair]
                    })
    
    # Role-level violations
    role_violations = []
    for role, tcodes in role_to_tcodes.items():
        for t1, t2 in combinations(tcodes, 2):
            pair = tuple(sorted((t1, t2)))
            if pair in conflict_risk_map:
                role_violations.append({
                    'ROLE': role,
                    'TCODE_1': pair[0],
                    'TCODE_2': pair[1],
                    'RISK_FACTOR': conflict_risk_map[pair]
                })
    
    return user_violations, role_violations

def create_excel_download(df, filename):
    """Create Excel file for download"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Violations')
    output.seek(0)
    return output

# =====================================================
# MAIN APPLICATION
# =====================================================
def main():
    
    # Header
    st.markdown('<div class="main-header">🔐 SAP SoD Risk Analysis System</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/security-shield-green.png", width=100)
        st.title("📋 Configuration")
        st.markdown("---")
        
        # Rule book upload
        st.subheader("1️⃣ Rule Book (Ground Truth)")
        rule_book_file = st.file_uploader(
            "Upload Rule Book Excel",
            type=['xlsx', 'xls'],
            key="rule_book",
            help="Fixed ground truth file containing conflict pairs"
        )
        
        st.markdown("---")
        
        # User access upload
        st.subheader("2️⃣ User Access Data")
        user_access_file = st.file_uploader(
            "Upload User Access Excel",
            type=['xlsx', 'xls'],
            key="user_access",
            help="Current user-role-authorization mappings"
        )
        
        st.markdown("---")
        st.info("📱 **Mobile Tip:** Tap 'Browse files' to select from your device")
        
    # Main content area
    if not rule_book_file:
        st.info("👈 **Step 1:** Upload the Rule Book file from the sidebar")
        st.markdown("""
        ### Welcome to SAP SoD Risk Analysis System
        
        This application helps you:
        - 🔍 Detect Segregation of Duties violations
        - 👥 Analyze user-level conflicts
        - 🎭 Analyze role-level conflicts
        - 📊 Visualize risk distributions
        - 📥 Download detailed reports
        
        **Get Started:**
        1. Upload Rule Book (ground truth)
        2. Upload User Access data
        3. Click "Analyze" to run the analysis
        """)
        return
    
    if not user_access_file:
        st.warning("📂 Rule Book uploaded successfully! Now upload User Access file.")
        return
    
    # Both files uploaded - show analysis button
    st.success("✅ Both files uploaded successfully!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 Run SoD Analysis", type="primary", use_container_width=True)
    
    if analyze_button:
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Load rule book
            status_text.text("📖 Loading rule book...")
            progress_bar.progress(10)
            rule_df = load_rule_book(rule_book_file)
            
            # Step 2: Process rule book
            status_text.text("🔧 Processing conflict pairs...")
            progress_bar.progress(25)
            conflict_risk_map = process_rule_book(rule_df)
            
            # Step 3: Load user access
            status_text.text("👥 Loading user access data...")
            progress_bar.progress(40)
            user_df = pd.read_excel(user_access_file)
            
            # Step 4: Process user access
            status_text.text("🗺️ Mapping users and roles...")
            progress_bar.progress(55)
            user_role_tcodes, role_to_tcodes = process_user_access(user_df)
            
            # Step 5: Analyze violations
            status_text.text("🔍 Analyzing SoD violations...")
            progress_bar.progress(75)
            user_violations, role_violations = analyze_violations(
                user_role_tcodes, role_to_tcodes, conflict_risk_map
            )
            
            # Step 6: Complete
            status_text.text("✅ Analysis complete!")
            progress_bar.progress(100)
            
            # Store results in session state
            st.session_state['analyzed'] = True
            st.session_state['conflict_pairs'] = len(conflict_risk_map)
            st.session_state['total_users'] = len(user_role_tcodes)
            st.session_state['total_roles'] = len(role_to_tcodes)
            st.session_state['user_violations'] = user_violations
            st.session_state['role_violations'] = role_violations
            st.session_state['user_violations_df'] = pd.DataFrame(user_violations) if user_violations else pd.DataFrame()
            st.session_state['role_violations_df'] = pd.DataFrame(role_violations) if role_violations else pd.DataFrame()
            
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            return
    
    # Display results if analysis has been run
    if st.session_state.get('analyzed', False):
        
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Ground Truth Pairs",
                value=f"{st.session_state['conflict_pairs']:,}"
            )
        
        with col2:
            st.metric(
                label="Total Users",
                value=f"{st.session_state['total_users']:,}"
            )
        
        with col3:
            st.metric(
                label="Total Roles",
                value=f"{st.session_state['total_roles']:,}"
            )
        
        with col4:
            st.metric(
                label="Total Violations",
                value=f"{len(st.session_state['user_violations']):,}",
                delta="User-Level"
            )
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["👥 User-Level Analysis", "🎭 Role-Level Analysis", "📈 Visualizations"])
        
        # TAB 1: User-Level
        with tab1:
            st.subheader("User-Level SoD Violations")
            
            if len(st.session_state['user_violations']) > 0:
                user_df = st.session_state['user_violations_df']
                
                # Risk summary
                col1, col2, col3 = st.columns(3)
                risk_counts = user_df['RISK_FACTOR'].value_counts()
                
                with col1:
                    high_count = risk_counts.get('High', 0)
                    st.metric("🔴 High Risk", f"{high_count:,}")
                
                with col2:
                    medium_count = risk_counts.get('Medium', 0)
                    st.metric("🟡 Medium Risk", f"{medium_count:,}")
                
                with col3:
                    low_count = risk_counts.get('Low', 0)
                    st.metric("🟢 Low Risk", f"{low_count:,}")
                
                # Download button
                st.markdown("---")
                user_excel = create_excel_download(user_df, "user_violations")
                st.download_button(
                    label="📥 Download User-Level Report (Excel)",
                    data=user_excel,
                    file_name=f"user_level_violations_{datetime.today().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                # Display table
                st.markdown("### Detailed Violations")
                st.dataframe(
                    user_df,
                    use_container_width=True,
                    height=400
                )
                
            else:
                st.success("✅ No user-level violations found!")
        
        # TAB 2: Role-Level
        with tab2:
            st.subheader("Role-Level SoD Violations")
            
            if len(st.session_state['role_violations']) > 0:
                role_df = st.session_state['role_violations_df']
                
                # Risk summary
                col1, col2, col3 = st.columns(3)
                risk_counts = role_df['RISK_FACTOR'].value_counts()
                
                with col1:
                    high_count = risk_counts.get('High', 0)
                    st.metric("🔴 High Risk", f"{high_count:,}")
                
                with col2:
                    medium_count = risk_counts.get('Medium', 0)
                    st.metric("🟡 Medium Risk", f"{medium_count:,}")
                
                with col3:
                    low_count = risk_counts.get('Low', 0)
                    st.metric("🟢 Low Risk", f"{low_count:,}")
                
                # Download button
                st.markdown("---")
                role_excel = create_excel_download(role_df, "role_violations")
                st.download_button(
                    label="📥 Download Role-Level Report (Excel)",
                    data=role_excel,
                    file_name=f"role_level_violations_{datetime.today().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                # Display table
                st.markdown("### Detailed Violations")
                st.dataframe(
                    role_df,
                    use_container_width=True,
                    height=400
                )
                
            else:
                st.success("✅ No role-level violations found!")
        
        # TAB 3: Visualizations
        with tab3:
            st.subheader("📈 Risk Analysis Visualizations")
            
            if len(st.session_state['user_violations']) > 0:
                
                col1, col2 = st.columns(2)
                
                # User violations by risk
                with col1:
                    user_df = st.session_state['user_violations_df']
                    risk_counts = user_df['RISK_FACTOR'].value_counts().reset_index()
                    risk_counts.columns = ['Risk Level', 'Count']
                    
                    fig1 = px.pie(
                        risk_counts,
                        values='Count',
                        names='Risk Level',
                        title='User Violations by Risk Level',
                        color='Risk Level',
                        color_discrete_map={'High': '#ff4444', 'Medium': '#ffaa00', 'Low': '#44ff44'}
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                # Role violations by risk
                with col2:
                    role_df = st.session_state['role_violations_df']
                    risk_counts = role_df['RISK_FACTOR'].value_counts().reset_index()
                    risk_counts.columns = ['Risk Level', 'Count']
                    
                    fig2 = px.pie(
                        risk_counts,
                        values='Count',
                        names='Risk Level',
                        title='Role Violations by Risk Level',
                        color='Risk Level',
                        color_discrete_map={'High': '#ff4444', 'Medium': '#ffaa00', 'Low': '#44ff44'}
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Top 10 high-risk users
                st.markdown("### 🔥 Top 10 High-Risk Users")
                user_df = st.session_state['user_violations_df']
                top_users = user_df['USER_NAME'].value_counts().head(10).reset_index()
                top_users.columns = ['User', 'Violations']
                
                fig3 = px.bar(
                    top_users,
                    x='Violations',
                    y='User',
                    orientation='h',
                    title='Users with Most Violations',
                    color='Violations',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig3, use_container_width=True)
                
                # Top 10 high-risk roles
                st.markdown("### 🎭 Top 10 High-Risk Roles")
                role_df = st.session_state['role_violations_df']
                top_roles = role_df['ROLE'].value_counts().head(10).reset_index()
                top_roles.columns = ['Role', 'Violations']
                
                fig4 = px.bar(
                    top_roles,
                    x='Violations',
                    y='Role',
                    orientation='h',
                    title='Roles with Most Violations',
                    color='Violations',
                    color_continuous_scale='Oranges'
                )
                st.plotly_chart(fig4, use_container_width=True)

# =====================================================
# RUN APPLICATION
# =====================================================
if __name__ == "__main__":
    main()
