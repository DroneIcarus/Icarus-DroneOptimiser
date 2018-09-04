using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Astar
{
    public partial class ASTAR : Form
    {
        public ASTAR()
        {
            InitializeComponent();

            blue = new SolidBrush(Color.Blue);
            bluePen = new Pen(blue, 1);
            gObject = this.CreateGraphics();
            lstLacs = new List<GraphNode>();

            initStartGoal();
        }

        private void initStartGoal()
        {
            Point pointInit = new Point(10, 10);
            gObject.FillEllipse(blue, new Rectangle(pointInit, new Size(10, 10)));

            addLac(lstLacs.Count, pointInit);

            Point pointFin = new Point(this.Size.Width - 100, this.Size.Height - 100);
            gObject.FillEllipse(blue, new Rectangle(pointFin, new Size(10, 10)));

            addLac(lstLacs.Count, pointFin);
        }


        private void writeToFile(String path, String text, Boolean Line, Boolean overwrite)
        {
            if (overwrite)
            {
                using (StreamWriter sw = File.CreateText(path))
                {
                    if (Line)
                    {
                        sw.WriteLine(text);
                    }
                    else
                    {
                        sw.Write(text);
                    }
                }
            }
            else if (File.Exists(path))
            {
                using (StreamWriter sw = File.AppendText(path))
                {
                    if (Line)
                    {
                        sw.WriteLine(text);
                    }
                    else
                    {
                        sw.Write(text);
                    }
                }
            }
        }


        private void resetPaint()
        {
            Point pointInit = new Point(10, 10);
            gObject.FillEllipse(blue, new Rectangle(pointInit, new Size(10, 10)));

            Point pointFin = new Point(this.Size.Width - 100, this.Size.Height - 100);
            gObject.FillEllipse(blue, new Rectangle(pointFin, new Size(10, 10)));


            foreach (GraphNode lac in lstLacs)
            {
                Point point = new Point(lac.getCurrent().posX, lac.getCurrent().posY);
                Size size = new Size(10, 10);
                gObject.FillEllipse(blue, new Rectangle(point, size));
            }

        }

        private void resetLacs()
        {
            GraphNode StartPosition = lstLacs.ElementAt(0);
            GraphNode GoalPosition = lstLacs.ElementAt(1);

            Console.Write("lac Count: ");
            Console.WriteLine(lstLacs.Count);

            //DateTime time = DateTime.Now;             // Use current time.
            //string format = "dd HH:mm";   // Use this format.

            string path = @"C:\Users\adri_\Desktop\nodes.txt";
            writeToFile(path, "", false,true);
            int i = 0;

            foreach (GraphNode lac1 in lstLacs)
            {
                lac1.setInitialHuristic(GoalPosition.getCurrent());
                Console.Write("lac id: ");
                Console.Write(lac1.getCurrent().id);
                Console.Write("initial heuristic: ");
                Console.WriteLine(lac1.getInitialHuristic());
                writeToFile(path, "id:" + lac1.getCurrent().id +",", false,false);
                writeToFile(path, "h:" + lac1.getInitialHuristic() + ",", false,false);

                lac1.ClearNeighbors();
                foreach (GraphNode lac2 in lstLacs)
                {
                    if (CalculateDistance(lac1.getCurrent(), lac2.getCurrent()) < Convert.ToDouble(textBox_distance.Text))
                    {
                        gObject.DrawLine(bluePen, lac1.getCurrent().posX, lac1.getCurrent().posY, lac2.getCurrent().posX, lac2.getCurrent().posY);
                        lac1.AddNeighbor(lac2.getCurrent());

                        writeToFile(path, "n:" + lac2.getCurrent().id + "c:" + CalculateDistance(lac1.getCurrent(), lac2.getCurrent()) + ",", false,false);
                    }
                }
                i++;

                if (lstLacs.Count > i)
                {
                    writeToFile(path, "", true, false);
                }
              
            }
        }

        private void Form1_Click(object sender, EventArgs e)
        {
            Point point = Cursor.Position;
            point.X -= this.Location.X+(this.Size.Width - this.ClientSize.Width);
            point.Y -= this.Location.Y+(this.Size.Height - this.ClientSize.Height);
            //Random rnd = new Random();

            Size size = new Size(10, 10);

            gObject.FillEllipse(blue, new Rectangle(point, size));

            addLac(lstLacs.Count, point);
        }

        private void addLac(int id, Point point)
        {
            Node value = new Node();
            value.id = id;
            value.posX = point.X;
            value.posY = point.Y;

            value.SizeX = 10;
            value.SizeY = 10;
            value.linkCost = 0;

            lstLacs.Add(new GraphNode(value));
        }

        private double CalculateDistance(Node node1, Node node2)
        {
            return  Math.Sqrt(Math.Pow(node1.posX - node2.posX, 2) + Math.Pow(node1.posY - node2.posY, 2));
        }

        private void button_link_Click(object sender, EventArgs e)
        {
            resetLacs();
        }

        private void button_findPath_Click(object sender, EventArgs e)
        {
            // A * 
            astar(lstLacs.ElementAt(0), lstLacs.ElementAt(1));
        }


        private int astar(GraphNode start, GraphNode goal)
        {
            // The set of currently discovered nodes that are not evaluated yet.
            // Initially, only the start node is known.

            Console.WriteLine("A* start");

            int CurrentSetIndex = 0;
            GraphNode current = null;
            GraphNode tempVal = null;
            List<int> OpenSet = new List<int>();
            List<int> CloseSet = new List<int>();

            OpenSet.Add(start.getCurrent().id);
            start.gScore = 0;
            start.fScore = GraphNode.setEstimateHurestic(start.getCurrent(),goal.getCurrent());

            Console.Write("Open Count = ");
            Console.WriteLine(OpenSet.Count);

            while (OpenSet.Count > 0) // while openSet is not empty
            {
                //current := the node in openSet having the lowest fScore[] value
                CurrentSetIndex = 0;
                current = lstLacs.ElementAt(OpenSet.ElementAt(CurrentSetIndex));

                int i = 0;

                foreach (int id_vertex in OpenSet)
                {
                    tempVal = lstLacs.ElementAt(id_vertex);

                    if (tempVal.fScore < current.fScore)
                    {
                        CurrentSetIndex = i;
                        current = lstLacs.ElementAt(id_vertex);
                    }
                    i++;
                }

                //if current = goal return reconstruct_path(cameFrom, current)
                if (current.getCurrent().id == goal.getCurrent().id)
                {
                    Console.WriteLine("A* end --> path found");
                    reconstruct_path(current.getCurrent().id);
                    return 0;
                }

                OpenSet.RemoveAt(CurrentSetIndex);
                Console.Write("Open Count = ");
                Console.WriteLine(OpenSet.Count);

                CloseSet.Add(current.getCurrent().id);

                Console.Write("Close Count = ");
                Console.WriteLine(CloseSet.Count);

                List<Node> neighbors = current.getNeighbors();

                foreach (Node neighbor in neighbors)
                {
                    bool close = false;
                    foreach (int id_vertex in CloseSet)
                    {
                        if (neighbor.id == id_vertex)
                        {
                            close = true;
                        }
                    }

                    if (!close)
                    {
                        if (!OpenSet.Equals(neighbor.id))
                        {
                            OpenSet.Add(neighbor.id);
                        }


                        int tentative_gScore = current.gScore + Node.getLinkCost(neighbor, goal.getCurrent());

                        if (tentative_gScore < lstLacs.ElementAt(neighbor.id).gScore)
                        {
                            lstLacs.ElementAt(neighbor.id).cameFrom = current.getCurrent().id;
                            lstLacs.ElementAt(neighbor.id).gScore = tentative_gScore;
                            lstLacs.ElementAt(neighbor.id).fScore = tentative_gScore + GraphNode.setEstimateHurestic(start.getCurrent(), goal.getCurrent());
                        }
                    }
                }

            }
            Console.WriteLine("A* end --> no path found");
            return 1;
        }


        private void reconstruct_path(int current)
        {
            List<int> total_path = new List<int>();

            total_path.Add(current);
            Console.WriteLine("Path end here");

            while (-1 != lstLacs.ElementAt(current).cameFrom)
            {
                Console.Write("path id: ");
                Console.WriteLine(current);
                current = lstLacs.ElementAt(current).cameFrom;
            }

            Console.Write("path id: ");
            Console.WriteLine(current);
            Console.WriteLine("Path start here");
        }


        public class Node {
            public int id;
            public int posX;
            public int posY;
            public int SizeX;
            public int SizeY;
            public int linkCost;
            private int heuristic;

            public void setLinkCost(Node endNode)
            {
                double temp1 = Math.Pow(Math.Abs(posX - endNode.posX), 2.0);
                double temp2 = Math.Pow(Math.Abs(posY - endNode.posY), 2.0);
                linkCost = (int)(temp1 + temp1);
            }


            public static int getLinkCost(Node current, Node voisin)
            {
                double temp1 = Math.Pow(Math.Abs(current.posX - voisin.posX), 2.0);
                double temp2 = Math.Pow(Math.Abs(current.posY - voisin.posY), 2.0);
                return (int)(temp1 + temp1);
            }

            public void setHurestic(Node endNode)
            {
                heuristic = Math.Abs(posX - endNode.posX) + Math.Abs(posY - endNode.posY);
            }

            public int getHurestic()
            {
                return heuristic;
            }

            public int getLinkCost()
            {
                return linkCost;
            }

        }

        public class GraphNode
        {
            private List<Node> neighbors;
            private Node CurrentNode;

            public int curID;
            public int cameFrom;
            public int gScore;
            public int fScore;

            public GraphNode(Node value)
            {
                CurrentNode = value;
                neighbors = new List<Node>();


                this.curID = value.id;
                cameFrom = -1;
                gScore = int.MaxValue;
                fScore = int.MaxValue;
            }

            public void AddNeighbor(Node value)
            {
                neighbors.Add(value);
                value.setLinkCost(CurrentNode);
            }

            public List<Node> getNeighbors()
            {
                return neighbors;
            }

            public void setInitialHuristic(Node goal)
            {
                CurrentNode.setHurestic(goal);
            }

            public int getInitialHuristic()
            {
                return CurrentNode.getHurestic();
            }

            public Node getNeighbor(int id)
            {
                return neighbors.ElementAt(id);
            }

            public Node getCurrent()
            {
                return CurrentNode;
            }

            public void ClearNeighbors()
            {
                neighbors.Clear();
            }

            public static int setEstimateHurestic(Node start, Node endNode)
            {
                return Math.Abs(start.posX - endNode.posX) + Math.Abs(start.posY - endNode.posY);
            }
        }

        private void button_clear_Click(object sender, EventArgs e)
        {
            lstLacs.Clear();
            gObject.Clear(Color.WhiteSmoke);
            initStartGoal();
        }

        private void ASTAR_Paint(object sender, PaintEventArgs e)
        {
            resetPaint();
        }


        List<GraphNode> lstLacs;
        Graphics gObject;
        Brush blue;
        Pen bluePen;

    }
}
