/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package routing;

import core.Connection;
import core.DTNHost;
import core.Settings;

/**
 *
 * @author Harold
 */
public class PropTTRRouterCentral extends PropTTRRouter {
    
    public static final String PROPTTRCENTRAL_NS = "PropTTRRouterCentral";
    
    public PropTTRRouterCentral(Settings settings) {
        super(settings);
        
    }
    
    protected PropTTRRouterCentral(PropTTRRouterCentral r) {
        super(r);
        this.TTR = -1;
    }
    
    @Override
    public void changedConnection(Connection con) {
            super.changedConnection(con);
            
            if (con.isUp()) { // new connection
			this.costsForMessages = null; // invalidate old cost estimates
			
			if (con.isInitiator(getHost())) {
				/* initiator performs all the actions on behalf of the
				 * other node too (so that the meeting probs are updated
				 * for both before exchanging them) */
				DTNHost otherHost = con.getOtherNode(getHost());
				MessageRouter mRouter = otherHost.getRouter();

				assert (mRouter instanceof PropTTRRouter) || (mRouter instanceof PropTTRRouterCentral): "PropTTR only works "+ 
				" with other routers of same type";
                                
                                if(mRouter instanceof PropTTRRouterCentral) {
                                    PropTTRRouter otherRouter = (PropTTRRouter)mRouter;
                                    otherRouter.seenCentralTimes.add(otherRouter.simulationTime);
                                    otherRouter.updateAvgSeenCentralTime();
                                    otherRouter.setTTRVal(otherRouter.averageSeenCentralTime);
                                }
                        }
            }
    }
    
    @Override
    public void setTTRVal(double val) { }
    
    
    @Override
    public MessageRouter replicate() {
            PropTTRRouterCentral r = new PropTTRRouterCentral(this);
            return r;
    }
}
