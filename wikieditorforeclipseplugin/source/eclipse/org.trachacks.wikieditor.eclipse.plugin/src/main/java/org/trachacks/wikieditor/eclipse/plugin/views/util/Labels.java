/**
 * 
 */
package org.trachacks.wikieditor.eclipse.plugin.views.util;

import java.util.MissingResourceException;
import java.util.ResourceBundle;

/**
 * @author ivan
 *
 */
public class Labels {

	private static ResourceBundle labels = ResourceBundle.getBundle(Labels.class.getName());
	
	public static String getText(String key) {
		try {
			return labels.getString(key);
		} catch (MissingResourceException e) {
			return key;
		}
	}

}
