style = """
    <style>
    /* Target the button when it is NOT disabled */
    div[data-testid="stButton"] button:not([disabled]) {
        background-color: #28a745 !important; /* Green background */
        color: white !important;               /* White text */
        border: none !important;
    }
    
    /* Optional: Change the green shade slightly on hover */
    div[data-testid="stButton"] button:not([disabled]):hover {
        background-color: #218838 !important; /* Darker green on hover */
        color: white !important;
    }
    </style>
    """