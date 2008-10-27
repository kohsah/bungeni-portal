/*
 * PersonSelector.java
 *
 * Created on August 12, 2008, 8:25 PM
 */

package org.bungeni.editor.selectors.debaterecord.speech;

import java.awt.Component;
import java.util.HashMap;
import org.bungeni.db.registryQueryDialog;
import org.bungeni.editor.selectors.BaseMetadataPanel;
import org.bungeni.ooo.OOComponentHelper;

/**
 *
 * @author  undesa
 */
public class PersonSelector extends  BaseMetadataPanel {
     registryQueryDialog rqs = null;
     private static org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(PersonSelector.class.getName());
 //    HashMap<String, String> selectionData = new HashMap<String,String>();
    
    /** Creates new form PersonSelector */
    public PersonSelector() {
        super();
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

        btn_SpeechBy = new javax.swing.JButton();

        setName("Person Selector"); // NOI18N

        btn_SpeechBy.setText("Select a Person...");
        btn_SpeechBy.setActionCommand("Select a Question");
        btn_SpeechBy.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btn_SpeechByActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addComponent(btn_SpeechBy)
                .addContainerGap(180, Short.MAX_VALUE))
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(btn_SpeechBy)
        );
    }// </editor-fold>//GEN-END:initComponents

private void btn_SpeechByActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btn_SpeechByActionPerformed
// TODO add your handling code here:
        rqs = new registryQueryDialog("Select A Person", "Select ID, FIRST_NAME, LAST_NAME, URI from persons", getParentFrame());
        rqs.show();
        log.debug("Moved on before closing child dialog");
        ((Main)getContainerPanel()).selectionData = rqs.getData();
        if (((Main)getContainerPanel()).selectionData.size() > 0 ) {
           // txt_SpeechBy.setText(selectionData.get("FIRST_NAME") + " " + selectionData.get("LAST_NAME"));
           // txt_URIofPerson.setText(selectionData.get("URI"));
            getContainerPanel().updateAllPanels();
        } else {
            log.debug("selected keyset empty");
        }
}//GEN-LAST:event_btn_SpeechByActionPerformed

      public String getPanelName() {
        return getName();
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
        String questionId = ((Main)getContainerPanel()).selectionData.get("ID");
        OOComponentHelper ooDoc = getContainerPanel().getOoDocument();
        HashMap<String,String> sectionMeta = new HashMap<String,String>();
        String newSectionName = ((Main)getContainerPanel()).mainSectionName;
        sectionMeta.put("BungeniQuestionNo", questionId);
        ooDoc.setSectionMetadataAttributes(newSectionName, sectionMeta);
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


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btn_SpeechBy;
    // End of variables declaration//GEN-END:variables

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
