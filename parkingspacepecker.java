import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.util.ArrayList;
import javax.swing.*;

public class ParkingSpaceStorer extends JFrame {

    private static final int WIDTH = 107;
    private static final int HEIGHT = 48;
    private static final String POSITIONS_FILE = "CarParkPos.ser";
    private static final String IMAGE_FILE = "carParkImg.jpeg";

    private ArrayList<Point> posList;
    private Image image;

    public ParkingSpaceStorer() {
        posList = loadPositions();

        // Load image
        image = Toolkit.getDefaultToolkit().getImage(IMAGE_FILE);

        // Set up frame
        setTitle("Parking Space Storer");
        setSize(image.getWidth(null), image.getHeight(null));
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setResizable(false);
        addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent e) {
                handleMouseClick(e);
            }
        });
    }

    private void handleMouseClick(MouseEvent e) {
        int x = e.getX();
        int y = e.getY();

        if (SwingUtilities.isLeftMouseButton(e)) {
            posList.add(new Point(x, y));
        } else if (SwingUtilities.isRightMouseButton(e)) {
            for (int i = 0; i < posList.size(); i++) {
                Point pos = posList.get(i);
                if (x > pos.x && x < pos.x + WIDTH && y > pos.y && y < pos.y + HEIGHT) {
                    posList.remove(i);
                    System.out.println("Deleted parking spot at: " + pos.x + ", " + pos.y);
                    break;
                }
            }
        }

        savePositions(posList);
        repaint();
    }

    public void paint(Graphics g) {
        super.paint(g);
        g.drawImage(image, 0, 0, this);
        g.setColor(Color.RED);

        for (Point pos : posList) {
            g.drawRect(pos.x, pos.y, WIDTH, HEIGHT);
        }
    }

    private ArrayList<Point> loadPositions() {
        ArrayList<Point> positions = new ArrayList<>();
        try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(POSITIONS_FILE))) {
            positions = (ArrayList<Point>) ois.readObject();
        } catch (Exception e) {
            System.out.println("Error loading positions file: " + e.getMessage());
        }
        return positions;
    }

    private void savePositions(ArrayList<Point> positions) {
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(POSITIONS_FILE))) {
            oos.writeObject(positions);
        } catch (Exception e) {
            System.out.println("Error saving positions file: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        EventQueue.invokeLater(() -> {
            ParkingSpaceStorer frame = new ParkingSpaceStorer();
            frame.setVisible(true);
        });
    }
}
