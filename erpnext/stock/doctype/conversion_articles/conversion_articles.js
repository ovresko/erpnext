// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Conversion Articles', {
	refresh: function(frm) {

	},
	convertir: function(frm){
		var lines = frm.doc.refs.split("\n");
		var old = "";
		for(var i = 0;i < lines.length;i++){
		    	//code here using lines[i] which will give you each line
			var ref = lines[i];
			console.log("red",ref);
			if(ref){
				var clean = ref.replace(/ /g,"").replace(/-/g,"").replace(/_/g,"").replace(/\//g,"").replace(/\./g,"");
				 
				console.log("clean",clean);
				
				if(clean){
					
					frappe.db.get_value('Item', {clean_manufacturer_part_number: clean}, ['item_code'], (r) => {
					if (r) {							
						old += "\n"+r.item_code; 
						console.log("item_code",r.item_code);
					}
					});
				}
				
			
			}
			
		}
		
		console.log("old",old);
		frm.set_value('codes', old);
		frm.refresh_fields();
	}
});
