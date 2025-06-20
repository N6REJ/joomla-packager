<?php
/**
 * @package     Joomla.Site
 * @subpackage  mod_test
 *
 * @copyright   Copyright (C) 2024 Test Company
 * @license     GNU General Public License version 2 or later
 * @version     1.0.0
 */

defined('_JEXEC') or die;

/**
 * Helper for mod_test
 *
 * @since  1.0.0
 */
class ModTestHelper
{
    /**
     * Module parameters
     *
     * @var    Registry
     * @since  1.0.0
     */
    protected $params;

    /**
     * Constructor
     *
     * @param   Registry  $params  The module parameters
     *
     * @since   1.0.0
     */
    public function __construct($params)
    {
        $this->params = $params;
    }

    /**
     * Get items to display
     *
     * @return  array
     *
     * @since   1.0.0
     */
    public function getItems()
    {
        return array(
            'message' => $this->params->get('test_param', 'Hello World')
        );
    }
}
