/*
 * QuestionSelect.java
 *
 * Created on August 12, 2008, 12:09 PM
 */

package org.bungeni.editor.selectors.debaterecord.question;

import java.awt.Component;
import java.util.HashMap;
import java.util.Set;
import org.bungeni.db.BungeniClientDB;
import org.bungeni.db.BungeniRegistryFactory;
import org.bungeni.db.GeneralQueryFactory;
import org.bungeni.db.QueryResults;
import org.bungeni.db.registryQueryDialog;
import org.bungeni.editor.selectors.BaseMetadataPanel;

/**
 *
 * @author  undesa
 */
public class QuestionSelect extends BaseMetadataPanel {
 
    registryQueryDialog rqs;
    private static org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(QuestionSelect.class.getName());
   // HashMap<String, String> selectionData = new HashMap<String,String>();
  
    /** Creates new form QuestionSelect */
    public QuestionSelect() {
        initComponents();
    }

    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        btnSelectQuestion = new javax.swing.JButton();

        setName("Select a Question"); // NOI18N

        btnSelectQuestion.setText("Select a Question...");
        btnSelectQuestion.setActionCommand("Select a Question");
        btnSelectQuestion.setName("btn_select_question"); // NOI18N
        btnSelectQuestion.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSelectQuestionActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addComponent(btnSelectQuestion)
                .addContainerGap(115, Short.MAX_VALUE))
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(btnSelectQuestion)
        );
    }// </editor-fold>//GEN-END:initComponents

private void btnSelectQuestionActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSelectQuestionActionPerformed
// TODO add your handling code here:
    
        rqs = new registryQueryDialog("Select A Question", "Select ID, QUESTION_TITLE, QUESTION_FROM, QUESTION_TO, QUESTON_TEXT as QUESTION_TEXT from questions", getParentFrame());
        rqs.show();
        log.debug("Moved on before closing child dialog");
       // HashMap<String,String> selectionData = ((Main)getContainerPanel()).selectionData;
        ((Main)getContainerPanel()).selectionData = rqs.getData();
        if ( ((Main)getContainerPanel()).selectionData.size() > 0 ) {
            HashMap<String,String> registryMap = BungeniRegistryFactory.fullConnectionString();  
            BungeniClientDB dbInstance = new BungeniClientDB(registryMap);
        
            Set keyset =  ((Main)getContainerPanel()).selectionData.keySet();
            log.debug("selected keyset size = " + keyset.size());
        //    txtQuestionTitle.setText(selectionData.get("QUESTION_TITLE"));
        //    txtAddressedTo.setText(selectionData.get("QUESTION_TO"));
            //resolve person name URI to registry entry
            ((Main)getContainerPanel()).updateAllPanels();
            //  txtPersonName.setText(fullName);
            
            //
           // txtQuestionText.setText(selectionData.get("QUESTON_TEXT"));
            //fillDocument();
        } else {
            log.debug("selected keyset empty");
        }
}//GEN-LAST:event_btnSelectQuestionActionPerformed


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnSelectQuestion;
    // End of variables declaration//GEN-END:variables

    public String getPanelName() {
        return "Title";
    }

    public Component getPanelComponent() {
        return this;
    }


    @Override
    public boolean doCancel() {
        return true;
    }

    @Override
    public boolean doReset() {
        return true;
    }

    @Override
    public boolean preFullEdit() {
        return true;
    }

    @Override
    public boolean processFullEdit() {
        return true;
    }

    @Override
    public boolean postFullEdit() {
        return true;
    }

    @Override
    public boolean preFullInsert() {
        return true;
    }

    @Override
    public boolean processFullInsert() {
        return true;
    }

    @Override
    public boolean postFullInsert() {
        return true;
    }

    @Override
    public boolean preSelectEdit() {
        return true;
    }

    @Override
    public boolean processSelectEdit() {
        return true;
    }

    @Override
    public boolean postSelectEdit() {
        return true;
    }

    @Override
    public boolean preSelectInsert() {
        return true;
    }

    @Override
    public boolean processSelectInsert() {
        return true;
    }

    @Override
    public boolean postSelectInsert() {
       return true;
    }

    @Override
    public boolean validateSelectedEdit() {
        return true;
    }

    @Override
    public boolean validateSelectedInsert() {
        return true;
    }

    @Override
    public boolean validateFullInsert() {
        return true;
    }

    @Override
    public boolean validateFullEdit() {
        return true;
    }
    
        @Override
    protected void initFieldsSelectedEdit() {
        return;
    }

    @Override
    protected void initFieldsSelectedInsert() {
        return;
    }

    @Override
    protected void initFieldsInsert() {
        return;
    }

    @Override
    protected void initFieldsEdit() {
        return;
    }
}
