package edu.lu.uni.serval.fixminer.akka.compare;

import com.github.gumtreediff.actions.ActionGenerator;
import com.github.gumtreediff.actions.model.Action;
import com.github.gumtreediff.matchers.Matcher;
import com.github.gumtreediff.matchers.Matchers;
import com.github.gumtreediff.tree.ITree;
import edu.lu.uni.serval.utils.EDiffHelper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

import java.util.List;
import java.util.Map;


/**
 * Created by anilkoyuncu on 03/04/2018.
 */
public class Compare {

    private Logger log = LoggerFactory.getLogger(Compare.class);


    public void coreCompare(String name, JedisPool innerPool, JedisPool outerPool) {

        Map<String, String> resultMap;
        Jedis jedis = null;
        ITree oldTree = null;
        ITree newTree = null;

        try {
            jedis = innerPool.getResource();

            String[] split = name.split("_");


            String i = split[1];
            String j = split[2];
            String keyName = split[0];


            oldTree = EDiffHelper.getSimpliedTree(keyName,i,outerPool);

            newTree = EDiffHelper.getSimpliedTree(keyName,j,outerPool);

            Matcher m = Matchers.getInstance().getMatcher(oldTree, newTree);
            m.match();


            ActionGenerator ag = new ActionGenerator(oldTree, newTree, m.getMappings());
            ag.generate();
            List<Action> actions = ag.getActions();

            double chawatheSimilarity1 = m.chawatheSimilarity(oldTree, newTree);
            String chawatheSimilarity = String.format("%1.2f", chawatheSimilarity1);
            double diceSimilarity1 = m.diceSimilarity(oldTree, newTree);
            String diceSimilarity = String.format("%1.2f", diceSimilarity1);
            double jaccardSimilarity1 = m.jaccardSimilarity(oldTree, newTree);
            String jaccardSimilarity = String.format("%1.2f", jaccardSimilarity1);

            String editDistance = String.valueOf(actions.size());

            String result = i + "," + j + "," + chawatheSimilarity + "," + diceSimilarity + "," + jaccardSimilarity + "," + editDistance;


            if (((Double) chawatheSimilarity1).equals(1.0) || ((Double) diceSimilarity1).equals(1.0)
                    || ((Double) jaccardSimilarity1).equals(1.0) || actions.size() == 0) {
                String matchKey = keyName+"_" + (String.valueOf(i)) + "_" + String.valueOf(j);
                log.info("{} tagged to be similar" ,matchKey);

                jedis.select(1);
                jedis.set(matchKey, result);

            }


            jedis.select(0);
            jedis.del(keyName+"_" + (String.valueOf(i)) + "_" + String.valueOf(j));



        } catch (Exception e) {

            log.debug("{} not comparable", name);
//            e.printStackTrace();


        }finally {
            if (jedis != null) {
                jedis.close();
            }
        }
    }


}
