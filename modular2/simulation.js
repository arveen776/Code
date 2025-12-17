import * as THREE from 'three';
import { World, Body, Box, Plane, Vec3, Material, NaiveBroadphase } from 'cannon-es';

// Configuration
const CUBE_SIZE = 0.5;
const CUBE_MASS = 1;
const GRAVITY = -9.82;
const MOVEMENT_FORCE = 50;
const ATTRACTION_FORCE = 30;
const DAMPING = 0.4;
const ASSEMBLY_THRESHOLD = 0.15; // Distance threshold for considering a cube "assembled"

// Global state
let scene, camera, renderer;
let world;
let cubes = [];
let cubeMeshes = [];
let targetShape = null;
let targetPositions = [];
let assembledCount = 0;
let startTime = null;
let isAssembling = false;
let animationId = null;

// Shape templates - define target positions relative to origin
const SHAPE_TEMPLATES = {
    cube: {
        name: 'Cube (3x3x3)',
        positions: (() => {
            const positions = [];
            const size = 3;
            const offset = (size - 1) * CUBE_SIZE * 0.5;
            for (let x = 0; x < size; x++) {
                for (let y = 0; y < size; y++) {
                    for (let z = 0; z < size; z++) {
                        positions.push({
                            x: x * CUBE_SIZE - offset,
                            y: y * CUBE_SIZE + CUBE_SIZE * 0.5,
                            z: z * CUBE_SIZE - offset
                        });
                    }
                }
            }
            return positions;
        })()
    },
    pyramid: {
        name: 'Pyramid',
        positions: (() => {
            const positions = [];
            const baseSize = 4;
            const offset = (baseSize - 1) * CUBE_SIZE * 0.5;
            for (let layer = 0; layer < baseSize; layer++) {
                const layerSize = baseSize - layer;
                const layerY = layer * CUBE_SIZE + CUBE_SIZE * 0.5;
                const layerOffset = (layerSize - 1) * CUBE_SIZE * 0.5;
                for (let x = 0; x < layerSize; x++) {
                    for (let z = 0; z < layerSize; z++) {
                        positions.push({
                            x: x * CUBE_SIZE - layerOffset,
                            y: layerY,
                            z: z * CUBE_SIZE - layerOffset
                        });
                    }
                }
            }
            return positions;
        })()
    },
    wall: {
        name: 'Wall (5x1x3)',
        positions: (() => {
            const positions = [];
            const width = 5;
            const height = 1;
            const depth = 3;
            const offsetX = (width - 1) * CUBE_SIZE * 0.5;
            const offsetZ = (depth - 1) * CUBE_SIZE * 0.5;
            for (let x = 0; x < width; x++) {
                for (let y = 0; y < height; y++) {
                    for (let z = 0; z < depth; z++) {
                        positions.push({
                            x: x * CUBE_SIZE - offsetX,
                            y: y * CUBE_SIZE + CUBE_SIZE * 0.5,
                            z: z * CUBE_SIZE - offsetZ
                        });
                    }
                }
            }
            return positions;
        })()
    },
    tower: {
        name: 'Tower (1x1x5)',
        positions: (() => {
            const positions = [];
            const height = 5;
            for (let y = 0; y < height; y++) {
                positions.push({
                    x: 0,
                    y: y * CUBE_SIZE + CUBE_SIZE * 0.5,
                    z: 0
                });
            }
            return positions;
        })()
    },
    'L-shape': {
        name: 'L-Shape',
        positions: (() => {
            const positions = [];
            // Vertical leg
            for (let y = 0; y < 4; y++) {
                positions.push({ x: 0, y: y * CUBE_SIZE + CUBE_SIZE * 0.5, z: 0 });
            }
            // Horizontal leg
            for (let x = 1; x < 4; x++) {
                positions.push({ x: x * CUBE_SIZE, y: CUBE_SIZE * 0.5, z: 0 });
            }
            return positions;
        })()
    },
    stairs: {
        name: 'Stairs',
        positions: (() => {
            const positions = [];
            const steps = 5;
            for (let i = 0; i < steps; i++) {
                for (let x = 0; x <= i; x++) {
                    positions.push({
                        x: x * CUBE_SIZE - (i * CUBE_SIZE * 0.5),
                        y: i * CUBE_SIZE + CUBE_SIZE * 0.5,
                        z: 0
                    });
                }
            }
            return positions;
        })()
    }
};

// Initialize Three.js scene
function initScene() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    scene.fog = new THREE.Fog(0x1a1a1a, 10, 50);

    // Camera
    camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.set(8, 8, 8);
    camera.lookAt(0, 0, 0);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.getElementById('canvas-container').appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 50;
    directionalLight.shadow.camera.left = -10;
    directionalLight.shadow.camera.right = 10;
    directionalLight.shadow.camera.top = 10;
    directionalLight.shadow.camera.bottom = -10;
    scene.add(directionalLight);

    const pointLight = new THREE.PointLight(0x4CAF50, 0.5);
    pointLight.position.set(0, 5, 0);
    scene.add(pointLight);

    // Ground plane
    const groundGeometry = new THREE.PlaneGeometry(30, 30);
    const groundMaterial = new THREE.MeshStandardMaterial({
        color: 0x2a2a2a,
        roughness: 0.8,
        metalness: 0.2
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = 0;
    ground.receiveShadow = true;
    scene.add(ground);

    // Grid helper
    const gridHelper = new THREE.GridHelper(30, 30, 0x444444, 0x222222);
    scene.add(gridHelper);

    // Initialize Cannon.js physics world
    world = new World();
    world.gravity.set(0, GRAVITY, 0);
    world.broadphase = new NaiveBroadphase();
    world.solver.iterations = 10;

    // Ground physics body
    const groundShape = new Plane();
    const groundBody = new Body({ mass: 0 });
    groundBody.addShape(groundShape);
    groundBody.quaternion.setFromAxisAngle(new Vec3(1, 0, 0), -Math.PI / 2);
    world.add(groundBody);

    // Handle window resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// Create a cube with physics
function createCube(position, index) {
    // Three.js mesh
    const geometry = new THREE.BoxGeometry(CUBE_SIZE, CUBE_SIZE, CUBE_SIZE);
    const material = new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL((index * 0.1) % 1, 0.7, 0.6),
        roughness: 0.5,
        metalness: 0.3
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.position.set(position.x, position.y, position.z);
    scene.add(mesh);

    // Cannon.js physics body
    const shape = new Box(new Vec3(CUBE_SIZE / 2, CUBE_SIZE / 2, CUBE_SIZE / 2));
    const body = new Body({ mass: CUBE_MASS });
    body.addShape(shape);
    body.position.set(position.x, position.y, position.z);
    body.material = new Material('cube');
    body.material.friction = 0.4;
    body.material.restitution = 0.3;
    body.linearDamping = DAMPING;
    body.angularDamping = DAMPING;
    world.add(body);

    // Store cube data
    const cube = {
        mesh,
        body,
        index,
        targetPosition: null,
        isAssembled: false,
        assemblyTime: null
    };

    cubes.push(cube);
    cubeMeshes.push(mesh);

    return cube;
}

// Initialize cubes in random positions
function initializeCubes(count) {
    // Clear existing cubes
    resetSimulation();

    const spreadRadius = 8;
    for (let i = 0; i < count; i++) {
        const angle = (i / count) * Math.PI * 2;
        const radius = 3 + Math.random() * spreadRadius;
        const height = 5 + Math.random() * 5;
        const position = {
            x: Math.cos(angle) * radius + (Math.random() - 0.5) * 2,
            y: height,
            z: Math.sin(angle) * radius + (Math.random() - 0.5) * 2
        };
        createCube(position, i);
    }

    document.getElementById('total').textContent = count;
    document.getElementById('assembled').textContent = '0';
}

// Set target shape and assign positions
function setTargetShape(shapeName) {
    const template = SHAPE_TEMPLATES[shapeName];
    if (!template) return;

    targetShape = shapeName;
    targetPositions = [...template.positions];

    // Shuffle target positions for more interesting assembly
    for (let i = targetPositions.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [targetPositions[i], targetPositions[j]] = [targetPositions[j], targetPositions[i]];
    }

    // Assign target positions to cubes
    cubes.forEach((cube, index) => {
        if (index < targetPositions.length) {
            cube.targetPosition = new Vec3(
                targetPositions[index].x,
                targetPositions[index].y,
                targetPositions[index].z
            );
        } else {
            // Extra cubes get random positions near the shape
            cube.targetPosition = new Vec3(
                (Math.random() - 0.5) * 5,
                0.5,
                (Math.random() - 0.5) * 5
            );
        }
        cube.isAssembled = false;
        cube.assemblyTime = null;
    });
}

// Apply autonomous movement forces to cubes
function applyAutonomousMovement() {
    if (!isAssembling) return;

    cubes.forEach((cube) => {
        if (cube.isAssembled || !cube.targetPosition) return;

        const body = cube.body;
        const currentPos = body.position;
        const targetPos = cube.targetPosition;

        // Calculate direction to target
        const direction = new Vec3();
        targetPos.vsub(currentPos, direction);
        const distance = direction.length();

        // If cube is close enough to target, consider it assembled
        if (distance < ASSEMBLY_THRESHOLD) {
            if (!cube.isAssembled) {
                cube.isAssembled = true;
                cube.assemblyTime = Date.now();
                assembledCount++;
                updateUI();
            }
            // Apply strong damping to keep it in place
            body.linearDamping = 0.9;
            body.angularDamping = 0.9;
            return;
        }

        // Normalize direction
        direction.normalize();

        // Calculate force based on distance (stronger when farther)
        const forceStrength = Math.min(ATTRACTION_FORCE * (distance / 5), MOVEMENT_FORCE);
        const force = direction.scale(forceStrength);

        // Apply horizontal movement force
        body.applyLocalForce(
            new Vec3(force.x, 0, force.z),
            new Vec3(0, 0, 0)
        );

        // Apply upward force if below target (helps cubes climb)
        if (currentPos.y < targetPos.y + 0.5) {
            const upwardForce = Math.min((targetPos.y - currentPos.y) * 20, 30);
            body.applyLocalForce(
                new Vec3(0, upwardForce, 0),
                new Vec3(0, 0, 0)
            );
        }

        // Add slight rotation to help with alignment
        if (distance > 0.5) {
            const rotationForce = 0.1;
            body.torque.set(
                (Math.random() - 0.5) * rotationForce,
                (Math.random() - 0.5) * rotationForce,
                (Math.random() - 0.5) * rotationForce
            );
        }
    });
}

// Update UI
function updateUI() {
    document.getElementById('assembled').textContent = assembledCount;
    const total = cubes.length;
    const percentage = total > 0 ? Math.round((assembledCount / total) * 100) : 0;
    
    if (isAssembling) {
        const elapsed = startTime ? ((Date.now() - startTime) / 1000).toFixed(1) : '0.0';
        document.getElementById('time').textContent = elapsed;
    }

    if (assembledCount === total && total > 0) {
        document.getElementById('status').textContent = 'Complete!';
        document.getElementById('status').style.color = '#4CAF50';
    } else if (isAssembling) {
        document.getElementById('status').textContent = `Assembling... ${percentage}%`;
        document.getElementById('status').style.color = '#ff9800';
    }
}

// Animation loop
function animate() {
    animationId = requestAnimationFrame(animate);

    // Step physics
    const timeStep = 1 / 60;
    world.step(timeStep);

    // Apply autonomous movement
    applyAutonomousMovement();

    // Update Three.js meshes to match physics bodies
    cubes.forEach((cube) => {
        cube.mesh.position.copy(cube.body.position);
        cube.mesh.quaternion.copy(cube.body.quaternion);

        // Visual feedback for assembled cubes
        if (cube.isAssembled) {
            cube.mesh.material.emissive = new THREE.Color(0x004400);
            cube.mesh.material.emissiveIntensity = 0.3;
        } else {
            cube.mesh.material.emissive = new THREE.Color(0x000000);
            cube.mesh.material.emissiveIntensity = 0;
        }
    });

    // Rotate camera around scene
    if (isAssembling) {
        const time = Date.now() * 0.0005;
        camera.position.x = Math.cos(time) * 12;
        camera.position.z = Math.sin(time) * 12;
        camera.position.y = 8 + Math.sin(time * 0.5) * 2;
        camera.lookAt(0, 2, 0);
    }

    renderer.render(scene, camera);
}

// Reset simulation
function resetSimulation() {
    // Remove all cubes
    cubes.forEach((cube) => {
        scene.remove(cube.mesh);
        world.remove(cube.body);
        cube.mesh.geometry.dispose();
        cube.mesh.material.dispose();
    });
    cubes = [];
    cubeMeshes = [];
    assembledCount = 0;
    isAssembling = false;
    startTime = null;
    targetShape = null;
    targetPositions = [];
    
    document.getElementById('status').textContent = 'Ready';
    document.getElementById('status').style.color = '#4CAF50';
    document.getElementById('assembled').textContent = '0';
    document.getElementById('time').textContent = '0.0';
}

// Start assembly
function startAssembly() {
    const shapeName = document.getElementById('shape-select').value;
    const cubeCount = parseInt(document.getElementById('cube-count').value);

    if (cubes.length === 0) {
        initializeCubes(cubeCount);
    }

    setTargetShape(shapeName);
    isAssembling = true;
    startTime = Date.now();
    assembledCount = 0;
    updateUI();

    document.getElementById('start-btn').disabled = true;
}

// Event listeners
document.getElementById('start-btn').addEventListener('click', startAssembly);
document.getElementById('reset-btn').addEventListener('click', () => {
    resetSimulation();
    document.getElementById('start-btn').disabled = false;
});

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        try {
            initScene();
            animate();
            console.log('Simulation initialized successfully');
        } catch (error) {
            console.error('Failed to initialize simulation:', error);
            document.body.innerHTML += '<div style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:red;color:white;padding:20px;z-index:10000;border-radius:10px;">Error loading simulation:<br>' + error.message + '<br><br>Check browser console for details</div>';
        }
    });
} else {
    try {
        initScene();
        animate();
        console.log('Simulation initialized successfully');
    } catch (error) {
        console.error('Failed to initialize simulation:', error);
        document.body.innerHTML += '<div style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:red;color:white;padding:20px;z-index:10000;border-radius:10px;">Error loading simulation:<br>' + error.message + '<br><br>Check browser console for details</div>';
    }
}

// Add keyboard controls for camera
let cameraControls = {
    distance: 12,
    angle: 0,
    height: 8
};

document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') cameraControls.angle -= 0.1;
    if (e.key === 'ArrowRight') cameraControls.angle += 0.1;
    if (e.key === 'ArrowUp') cameraControls.height += 1;
    if (e.key === 'ArrowDown') cameraControls.height -= 1;
});

