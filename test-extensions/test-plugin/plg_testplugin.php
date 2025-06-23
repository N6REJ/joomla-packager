<?php
/**
 * @package     Joomla.Plugin
 * @subpackage  System.testplugin
 *
 * @copyright   Copyright (C) 2024 Test. All rights reserved.
 * @license     GNU General Public License version 2 or later; see LICENSE.txt
 */

defined('_JEXEC') or die;

use Joomla\CMS\Plugin\CMSPlugin;

class PlgSystemTestplugin extends CMSPlugin
{
    public function onAfterInitialise()
    {
        // Simple test message in the debug log
        \Joomla\CMS\Factory::getApplication()->enqueueMessage('Test Plugin is active!', 'info');
    }
}
