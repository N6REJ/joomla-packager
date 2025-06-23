<?php
/**
 * @package     Joomla.Site
 * @subpackage  com_testcomponent
 *
 * @copyright   Copyright (C) 2024 Test. All rights reserved.
 * @license     GNU General Public License version 2 or later; see LICENSE.txt
 */

defined('_JEXEC') or die;

use Joomla\CMS\Component\ComponentHelper;
use Joomla\CMS\Factory;

// Simple dispatcher for demonstration
$controller = JControllerLegacy::getInstance('Testcomponent');
$controller->execute(Factory::getApplication()->input->get('task'));
$controller->redirect();
