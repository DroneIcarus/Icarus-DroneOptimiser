namespace Astar
{
    partial class ASTAR
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.button_link = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.textBox_distance = new System.Windows.Forms.TextBox();
            this.button_findPath = new System.Windows.Forms.Button();
            this.button_clear = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // button_link
            // 
            this.button_link.Location = new System.Drawing.Point(2, 546);
            this.button_link.Name = "button_link";
            this.button_link.Size = new System.Drawing.Size(75, 23);
            this.button_link.TabIndex = 0;
            this.button_link.Text = "faire les liens";
            this.button_link.UseVisualStyleBackColor = true;
            this.button_link.Click += new System.EventHandler(this.button_link_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(83, 551);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(69, 13);
            this.label1.TabIndex = 1;
            this.label1.Text = "distance max";
            // 
            // textBox_distance
            // 
            this.textBox_distance.ImeMode = System.Windows.Forms.ImeMode.Alpha;
            this.textBox_distance.Location = new System.Drawing.Point(158, 548);
            this.textBox_distance.Name = "textBox_distance";
            this.textBox_distance.Size = new System.Drawing.Size(100, 20);
            this.textBox_distance.TabIndex = 2;
            this.textBox_distance.Text = "150";
            // 
            // button_findPath
            // 
            this.button_findPath.Location = new System.Drawing.Point(264, 546);
            this.button_findPath.Name = "button_findPath";
            this.button_findPath.Size = new System.Drawing.Size(108, 23);
            this.button_findPath.TabIndex = 3;
            this.button_findPath.Text = "Meilleur chemin";
            this.button_findPath.UseVisualStyleBackColor = true;
            this.button_findPath.Click += new System.EventHandler(this.button_findPath_Click);
            // 
            // button_clear
            // 
            this.button_clear.Location = new System.Drawing.Point(378, 546);
            this.button_clear.Name = "button_clear";
            this.button_clear.Size = new System.Drawing.Size(110, 23);
            this.button_clear.TabIndex = 4;
            this.button_clear.Text = "Effacer";
            this.button_clear.UseVisualStyleBackColor = true;
            this.button_clear.Click += new System.EventHandler(this.button_clear_Click);
            // 
            // ASTAR
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(928, 571);
            this.Controls.Add(this.button_clear);
            this.Controls.Add(this.button_findPath);
            this.Controls.Add(this.textBox_distance);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.button_link);
            this.Name = "ASTAR";
            this.Text = "ASTAR";
            this.Click += new System.EventHandler(this.Form1_Click);
            this.Paint += new System.Windows.Forms.PaintEventHandler(this.ASTAR_Paint);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button button_link;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox textBox_distance;
        private System.Windows.Forms.Button button_findPath;
        private System.Windows.Forms.Button button_clear;
    }
}

