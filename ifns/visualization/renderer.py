import logging
from pathlib import Path
import ROOT


class RootRenderer:
    """ Handles plotting and saving.
    """
    
    @staticmethod
    def draw_and_save(obj, output_file: str | Path, x_min: float | None = None, x_max: float | None = None):
        """ Draws a TH1F or a TGraph.
        """
        ROOT.gStyle.SetOptStat(1111)  # Shows Entries, Average, RMS
        ROOT.gStyle.SetOptFit(1111)   # Shows fit parameters (if present)
        # Define the canvas
        canvas = ROOT.TCanvas("c1", "Canvas", 1920, 1080)
        # Common estetic settings
        obj.SetLineColor(ROOT.kBlue)
        obj.SetMarkerStyle(20)
        obj.SetMarkerSize(0.8)
        obj.SetMarkerColor(ROOT.kBlack)
        if isinstance(obj, ROOT.TH1):
            if x_min is not None and x_max is not None:
                obj.GetXaxis().SetRangeUser(x_min, x_max)
            # Draw error bars
            obj.Draw('E1')
        elif isinstance(obj, ROOT.TGraph) or isinstance(obj, ROOT.TGraphErrors):
            if x_min is not None and x_max is not None:
                obj.GetXaxis().SetLimits(x_min, x_max)
            # A = Axes, P = Points, E = Error bars
            obj.Draw("APE")
        # Force an update so the stat box is actually generated in memory
        canvas.Update()
        # Retrieve the stat box
        # For histograms, it's attached to the list of functions
        st = obj.GetListOfFunctions().FindObject("stats") 
        if st:
            # Set relative coordinates (NDC)
            # (X1, Y1) is bottom-left, (X2, Y2) is top-right
            st.SetX1NDC(0.70)  # Left edge starts at 70% of canvas width
            st.SetX2NDC(0.90)  # Right edge ends at 90%
            st.SetY1NDC(0.70)  # Bottom edge starts at 70% of canvas height
            st.SetY2NDC(0.90)  # Top edge ends at 90%
            st.SetTextSize(0.025) # Clean, readable font size
        # Save the file
        safe_output_file = str(output_file)
        canvas.SaveAs(safe_output_file)
        logging.info(f"Plot saved in: {safe_output_file}")
        # Prevent memory leaks
        canvas.Close()