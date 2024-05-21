/* 
 * Copyright 2010 Aalto University, ComNet
 * Released under GPLv3. See LICENSE.txt for details. 
 */
package movement;

import java.util.List;

import movement.map.DijkstraPathFinder;
import movement.map.MapNode;
import movement.map.PointsOfInterest;
import core.Settings;
import core.Coord;
import routing.PropTTRRouter;

/**
 * Map based movement model that uses Dijkstra's algorithm to find shortest
 * paths between two random map nodes and Points Of Interest
 */
public class ShortestPathMapAndTTRBasedMovement extends MapBasedMovement implements 
	SwitchableMovement {
	/** the Dijkstra shortest path finder */
	private DijkstraPathFinder pathFinder;

	/** Points Of Interest handler */
	private PointsOfInterest pois;
        
        private PointsOfInterest pois_libres;
	
	/**
	 * Creates a new movement model based on a Settings object's settings.
	 * @param settings The Settings object where the settings are read from
	 */
	public ShortestPathMapAndTTRBasedMovement(Settings settings) {
		super(settings);
		this.pathFinder = new DijkstraPathFinder(getOkMapNodeTypes());
		this.pois = new PointsOfInterest(getMap(), getOkMapNodeTypes(),
				settings, rng);
                pois_libres = new PointsOfInterest(getMap(), getOkMapNodeTypes(), new Settings(), rng);
	}
	
	/**
	 * Copyconstructor.
	 * @param mbm The ShortestPathMapAndTTRBasedMovement prototype to base 
	 * the new object to 
	 */
	protected ShortestPathMapAndTTRBasedMovement(ShortestPathMapAndTTRBasedMovement mbm) {
		super(mbm);
		this.pathFinder = mbm.pathFinder;
		this.pois = mbm.pois;
                this.pois_libres = mbm.pois_libres;
	}
	
	@Override
	public Path getPath() {
                double rapidez = generateSpeed();
		Path p = new Path(rapidez);
                MapNode to_base = pois.selectDestination();
		MapNode to = pois_libres.selectDestination();
		List<MapNode> nodePath = pathFinder.getShortestPath(lastMapNode, to);
                double totalDistance = 0;
                Coord lastCoord = nodePath.get(0).getLocation();
                for(int i=1; i<nodePath.size(); i++) {
                    totalDistance += lastCoord.distance(nodePath.get(i).getLocation());
                    lastCoord = nodePath.get(i).getLocation();
                }
                if(totalDistance/rapidez > ((PropTTRRouter)getHost().getRouter()).getTTR()) {
                    to = to_base; // de vuelta a base station
                    nodePath = pathFinder.getShortestPath(lastMapNode, to);
                    System.out.println(to);
                }
                //System.out.println("Distancia total: " + totalDistance);
                //System.out.println("Tiempo a gastar: " + totalDistance/rapidez);
		
		// this assertion should never fire if the map is checked in read phase
		assert nodePath.size() > 0 : "No path from " + lastMapNode + " to " +
			to + ". The simulation map isn't fully connected";
				
		for (MapNode node : nodePath) { // create a Path from the shortest path
			p.addWaypoint(node.getLocation());
		}
		
		lastMapNode = to;
		
		return p;
	}	
	
	@Override
	public ShortestPathMapAndTTRBasedMovement replicate() {
		return new ShortestPathMapAndTTRBasedMovement(this);
	}

}
