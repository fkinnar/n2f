SELECT AdresseEmail
      ,Prenom
      ,Nom
      ,Entreprise
      ,Fonction
      ,Role
      ,Profil
      ,Manager
      ,Compte_Auxiliaire_Agresso
      ,Moyen_Paiement_Prof
      ,Compte_Auxiliaire2
      ,Matricule
      ,Centre_Cout
      ,Creation_Vehicule
      ,Appro_Veh_Adm
      ,Deduction_Distance_TravDom
      ,Distance_TravDom
      ,Devise
      ,langue
      ,Structure
      ,Champs_Liaison_SSO
      ,Droit_Relever_Plafond
      ,Methode_SSO
      ,Update_Champs_Perso
      ,Nouveau_Email
      ,Action
      ,CompanyID
      ,LocationID
      ,DivisionID
FROM iris_N2F_User
WHERE LOWER(AdresseEmail) IN (
      -- 'fabrice.kinnar@iris.be',
      'thierry.bontinck@iris.be',
      'christophe.mardaga@iris.be',
      'olena.opriatnova@iris.be',
      'loqmane.bouzrouti@iris.be',
      'yves.rome@iris.be',
      'chantal.willems@iris.be',
      'xavier.thomas@iris.be'
)
ORDER BY AdresseEmail ASC
