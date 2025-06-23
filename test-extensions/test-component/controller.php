<?php
/**
 * @package     Joomla.Site
 * @subpackage  com_testcomponent
 * @copyright   Copyright (C) 2024 Test. All rights reserved.
 * @license     GNU General Public License version 2 or later; see LICENSE.txt
 */

defined('_JEXEC') or die;

class TestcomponentController extends JControllerLegacy
{
    public function display($cachable = false, $urlparams = array())
    {
        $view = $this->input->getCmd('view', 'default');
        parent::display();
    }
}
