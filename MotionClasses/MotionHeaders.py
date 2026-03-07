class MotionHeaders:
	MOTION_NAME: str = 'motionName'
	FRAME_NUMBER: str = 'frameNumber'
	SPEED_X: str = 'speedX'
	SPEED_Y: str = 'speedY'
	HIT_AREA_LEFT: str = 'hitAreaLeft'
	HIT_AREA_RIGHT: str = 'hitAreaRight'
	HIT_AREA_UP: str = 'hitAreaUp'
	HIT_AREA_DOWN: str = 'hitAreaDown'
	STATE: str = 'state'
	ATTACK_HIT_AREA_LEFT: str = 'attack.hitAreaLeft'
	ATTACK_HIT_AREA_RIGHT: str = 'attack.hitAreaRight'
	ATTACK_HIT_AREA_UP: str = 'attack.hitAreaUp'
	ATTACK_HIT_AREA_DOWN: str = 'attack.hitAreaDown'
	ATTACK_SPEED_X: str = 'attack.speedX'
	ATTACK_SPEED_Y: str = 'attack.speedY'
	ATTACK_START_UP: str = 'attack.StartUp'
	ATTACK_ACTIVE: str = 'attack.Active'
	ATTACK_HIT_DAMAGE: str = 'attack.HitDamage'
	ATTACK_GUARD_DAMAGE: str = 'attack.GuardDamage'
	ATTACK_START_ADD_ENERGY: str = 'attack.StartAddEnergy'
	ATTACK_HIT_ADD_ENERGY: str = 'attack.HitAddEnergy'
	ATTACK_GUARD_ADD_ENERGY: str = 'attack.GuardAddEnergy'
	ATTACK_GIVE_ENERGY: str = 'attack.GiveEnergy'
	ATTACK_IMPACT_X: str = 'attack.ImpactX'
	ATTACK_IMPACT_Y: str = 'attack.ImpactY'
	ATTACK_GIVE_GUARD_RECOV: str = 'attack.GiveGuardRecov'
	ATTACK_ATTACK_TYPE: str = 'attack.AttackType'
	ATTACK_DOWN_PROP: str = 'attack.DownProp'
	CANCEL_ABLE_FRAME: str = 'cancelAbleFrame'
	CANCEL_ABLE_MOTION_LEVEL: str = 'cancelAbleMotionLevel'
	MOTION_LEVEL: str = 'motionLevel'
	CONTROL: str = 'control'
	LANDING_FLAG: str = 'landingFlag'
	IMAGE: str = 'Image'

	D_TYPE = {
		MOTION_NAME: 'string',
		FRAME_NUMBER: 'int16',
		SPEED_X: 'int16',
		SPEED_Y: 'int16',
		HIT_AREA_LEFT: 'int16',
		HIT_AREA_RIGHT: 'int16',
		HIT_AREA_UP: 'int16',
		HIT_AREA_DOWN: 'int16',
		STATE: 'string',
		ATTACK_HIT_AREA_LEFT: 'int16',
		ATTACK_HIT_AREA_RIGHT: 'int16',
		ATTACK_HIT_AREA_UP: 'int16',
		ATTACK_HIT_AREA_DOWN: 'int16',
		ATTACK_SPEED_X: 'int16',
		ATTACK_SPEED_Y: 'int16',
		ATTACK_START_UP: 'int16',
		ATTACK_ACTIVE: 'int16',
		ATTACK_HIT_DAMAGE: 'int16',
		ATTACK_GUARD_DAMAGE: 'int16',
		ATTACK_START_ADD_ENERGY: 'int16',
		ATTACK_HIT_ADD_ENERGY: 'int16',
		ATTACK_GUARD_ADD_ENERGY: 'int16',
		ATTACK_GIVE_ENERGY: 'int16',
		ATTACK_IMPACT_X: 'int16',
		ATTACK_IMPACT_Y: 'int16',
		ATTACK_GIVE_GUARD_RECOV: 'int16',
		ATTACK_ATTACK_TYPE: 'int16',
		ATTACK_DOWN_PROP: 'boolean',
		CANCEL_ABLE_FRAME: 'int16',
		CANCEL_ABLE_MOTION_LEVEL: 'int16',
		MOTION_LEVEL: 'int16',
		CONTROL: 'boolean',
		LANDING_FLAG: 'boolean',
		IMAGE: 'string',
	}
